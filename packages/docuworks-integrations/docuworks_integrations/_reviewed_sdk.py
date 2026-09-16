"""Native boundary for blank reviews. Imported only when a native operation runs."""
import ctypes
import json
import shutil
from pathlib import Path

from docuworks_ctypes.document import Annotation, Page
from docuworks_ctypes.errors import XdwError
from docuworks_ctypes._raw.constants import XDW_E_INVALIDARG

DOC_ATTRIBUTE = b'DW-OCR.SessionDocument'
PAGE_ATTRIBUTE = b'DW-OCR.SessionPage'
TEXT_ATTRIBUTE = b'DW-OCR.SessionText'


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')


class _BlankReviewPage(Page):
    """Append hint for one exclusively owned blank Review page during creation.

    Keep actual SDK annotation information and all inherited value validation.
    A hint mismatch disables the shortcut for this page and uses Core's search.
    Never retain this object across page edits, deletes, or document reopening.
    """

    def __init__(self, page):
        super().__init__(page.document, page.number)
        self._next_index = 1 if self._page_info().nAnnotations == 0 else None

    def _refresh_added_annotation(self, new_handle, *, parent=None):
        if parent is None and self._next_index is not None:
            try:
                info = self._get_annotation_info(None, self._next_index)
            except XdwError as error:
                if error.result != XDW_E_INVALIDARG:
                    raise
            else:
                if info.handle == new_handle.value:
                    self._next_index += 1
                    return Annotation(self, info)
        self._next_index = None
        return super()._refresh_added_annotation(new_handle, parent=parent)


class ReviewSdk:
    def __init__(self, dll_path):
        from docuworks_ctypes import XdwApi
        self.api = XdwApi.load(dll_path)

    @staticmethod
    def attribute(function, *args):
        from docuworks_ctypes._raw.constants import XDW_E_INVALIDARG
        from docuworks_ctypes.errors import check_result
        size = function(*args, None, 0, None)
        if size == XDW_E_INVALIDARG:
            return None
        check_result(size, 'review attribute size')
        if size > 1024 * 1024:
            raise ValueError('review attribute exceeds 1 MiB')
        buffer = (ctypes.c_char * size)()
        actual = function(*args, buffer, size, None)
        check_result(actual, 'review attribute data')
        if actual != size:
            raise RuntimeError('review attribute changed while reading')
        return bytes(buffer)

    def inspect(self, path):
        from docuworks_ctypes import AnnotationType
        from docuworks_ctypes._raw import types as T
        from docuworks_ctypes.errors import check_result
        result = {'pages': []}
        with self.api.open_document(path) as doc:
            result['identity'] = self.attribute(doc.raw.XDW_GetUserAttribute, doc.handle, DOC_ATTRIBUTE)
            for n in range(1, doc.page_count + 1):
                info = T.XDW_PAGE_INFO_EX()
                info.nSize = ctypes.sizeof(info)
                check_result(doc.raw.XDW_GetPageInformation(doc.handle, n,
                             ctypes.cast(ctypes.byref(info), ctypes.POINTER(T.XDW_PAGE_INFO))), 'review page info')
                page = doc.page(n)
                record = dict(page=n, width_mm=info.nWidth / 100, height_mm=info.nHeight / 100,
                              rotation=info.nDegree, identity=self.attribute(doc.raw.XDW_GetPageUserAttribute,
                              doc.handle, n, PAGE_ATTRIBUTE), items=[])
                for annotation in page.annotations(recursive=False):
                    for child in annotation.descendants():
                        if child.annotation_type == AnnotationType.TEXT:
                            raise ValueError(f'page {n}: nested text in a group/sticky annotation is unsupported')
                    if annotation.annotation_type != AnnotationType.TEXT:
                        continue
                    a = annotation._info
                    record['items'].append(dict(
                        text=annotation.get_standard_attribute('%Text'), x=a.nHorPos / 100,
                        y=a.nVerPos / 100, width=a.nWidth / 100, height=a.nHeight / 100,
                        rotation=annotation.get_standard_attribute_raw('%TextOrientation'),
                        direction=annotation.get_standard_attribute_raw('%TextDirection'),
                        font_name=annotation.get_standard_attribute('%FontName'),
                        font_size=annotation.get_standard_attribute('%FontSize'),
                        fore_color=annotation.get_standard_attribute_raw('%ForeColor'),
                        word_wrap=annotation.get_standard_attribute('%WordWrap'),
                        identity=self.attribute(doc.raw.XDW_GetAnnotationUserAttribute,
                                                annotation.handle, TEXT_ATTRIBUTE)))
                result['pages'].append(record)
        return result

    def source_pages(self, path):
        with self.api.open_document(path) as doc:
            return [(p._page_info().nWidth / 100, p._page_info().nHeight / 100)
                    for p in (doc.page(n) for n in range(1, doc.page_count + 1))]

    def create(self, identity, identity_hash, output):
        from PIL import Image
        from docuworks_ctypes import OpenMode, PointMM, Color
        from docuworks_ctypes._raw import types as T, constants as C
        from docuworks_ctypes.encoding import wchar_buffer
        from docuworks_ctypes.errors import check_result
        output = Path(output)
        white = output.parent / 'white.bmp'
        Image.new('1', (100, 100), 1).save(white, dpi=(100, 100))
        parts = []
        for p in identity['pages']:
            part = output.parent / f"blank-{p['page']}.xdw"
            options = T.XDW_CREATE_OPTION()
            options.nSize = ctypes.sizeof(options)
            options.nFitImage = C.XDW_CREATE_USERDEF
            options.nWidth = round(p['width_mm'] * 100)
            options.nHeight = round(p['height_mm'] * 100)
            options.nZoom = 100
            check_result(self.api.raw.XDW_CreateXdwFromImageFileW(wchar_buffer(str(white)),
                         wchar_buffer(str(part)), ctypes.byref(options)), 'create blank review page')
            parts.append(part)
        shutil.copyfile(parts[0], output)
        common = dict(review_id=identity['review_id'], identity_sha256=identity_hash)
        with self.api.open_document(output, mode=OpenMode.UPDATE) as doc:
            for n, part in enumerate(parts[1:], 2):
                check_result(doc.raw.XDW_InsertDocumentW(doc.handle, n, wchar_buffer(str(part)), None), 'insert review page')
            value = encoded(common)
            check_result(doc.raw.XDW_SetUserAttribute(doc.handle, DOC_ATTRIBUTE, value, len(value), None), 'set review document identity')
            for p in identity['pages']:
                value = encoded(dict(common, page_id=p['page_id']))
                check_result(doc.raw.XDW_SetPageUserAttribute(doc.handle, p['page'], PAGE_ATTRIBUTE,
                             value, len(value), None), 'set review page identity')
                page = _BlankReviewPage(doc.page(p['page'])) if p['items'] else None
                for source in p['items']:
                    a = page.add_text(PointMM(source['x'], source['y']), source['text'],
                                                   font_size=12, fore_color=Color.RED, back_color=Color.NONE)
                    a.set_standard_attribute_raw('%TextDirection', 0)
                    a.set_standard_attribute_raw('%TextOrientation', 0)
                    a.set_standard_attribute('%WordWrap', False)
                    a.set_user_attribute(TEXT_ATTRIBUTE.decode('ascii'), encoded(dict(common,
                                         annotation_id=source['annotation_id'], region_id=source['region_id'])))
            doc.save()
        # These temporary inputs were created solely by this invocation.
        for part in parts:
            part.unlink()
        white.unlink()
        import platform
        return dict(python=platform.python_version(), platform=platform.platform(),
                    api_version=self.api.runtime_info.version_text,
                    dll_sha256=self.api.runtime_info.dll_sha256)

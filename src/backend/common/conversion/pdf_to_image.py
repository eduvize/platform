from typing import List
import io
from pdf2image import convert_from_bytes

def get_images_from_pdf_bytes(pdf_bytes: bytes) -> List[bytes]:
    """
    Convert a PDF file to a list of images in bytes format.

    Args:
        pdf_bytes (bytes): The PDF file in bytes format.

    Returns:
        List[bytes]: A list of images in PNG bytes format.
    """
    images = convert_from_bytes(pdf_bytes)
    pngs = []
    
    for image in images:
        with io.BytesIO() as output:
            image.save(output, format="PNG")
            pngs.append(output.getvalue())
            
    return pngs
from typing import List
import io
import asyncio
from pdf2image import convert_from_bytes

async def get_images_from_pdf_bytes(pdf_bytes: bytes) -> List[bytes]:
    """
    Convert a PDF file to a list of images in bytes format asynchronously.

    Args:
        pdf_bytes (bytes): The PDF file in bytes format.

    Returns:
        List[bytes]: A list of images in PNG bytes format.
    """
    def convert_pdf():
        return convert_from_bytes(pdf_bytes)

    images = await asyncio.to_thread(convert_pdf)
    pngs = []
    
    async def save_image(image):
        with io.BytesIO() as output:
            image.save(output, format="PNG")
            return output.getvalue()

    pngs = await asyncio.gather(*[save_image(image) for image in images])
            
    return pngs
"""Embeds the ZUGFeRD/Factur-X CII XML into a plain PDF, producing a
PDF/A-3 container with the required XMP metadata
(fx:DocumentType, fx:DocumentFileName, fx:Version, fx:ConformanceLevel),
per SPEC.md §4.3.
"""

from facturx import generate_from_binary


def embed_zugferd_xml(pdf_bytes: bytes, xml_bytes: bytes) -> bytes:
    return generate_from_binary(
        pdf_bytes,
        xml_bytes,
        flavor="factur-x",
        level="en16931",
        check_xsd=True,
    )

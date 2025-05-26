using System.Collections.Generic;

namespace PdfRenderer.Models;

public class CombineRequest
{
    public required List<string> PdfBase64 { get; set; }
}


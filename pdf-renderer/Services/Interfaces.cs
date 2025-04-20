using System.Collections.Generic;
using System.Threading.Tasks;

namespace PdfRenderer.Services
{
    public interface IPdfRenderService
    {
        byte[] RenderPdf(List<string> htmlPages, List<string> baseUris, Dictionary<string, string> settings);
    }

    public interface IPreviewService
    {
        Task<string> GeneratePreviewAsync(byte[] pdfBytes);
    }
} 
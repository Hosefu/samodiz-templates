using Microsoft.AspNetCore.Mvc;
using PdfRenderer.Models;
using PdfRenderer.Services;
using Microsoft.Extensions.Logging;
using System.Threading.Tasks;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace PdfRenderer.Controllers;

[ApiController]
public class PdfController : ControllerBase
{
    private readonly ILogger<PdfController> _logger;
    private readonly PdfRenderService _pdfRenderService;

    public PdfController(
        ILogger<PdfController> logger,
        PdfRenderService pdfRenderService)
    {
        _logger = logger;
        _pdfRenderService = pdfRenderService;
    }

    [HttpGet("health")]
    public IActionResult HealthCheck()
    {
        return Ok(new { 
            status = "healthy", 
            service = "pdf-renderer",
            version = "1.0.0"
        });
    }

    [HttpPost("api/render")]
    [Consumes("application/json")]
    [Produces("application/pdf")]
    public async Task<IActionResult> Render([FromBody] RenderRequest request)
    {
        try
        {
            _logger.LogInformation("Received rendering request");
            
            // Validation
            if (string.IsNullOrWhiteSpace(request.Html))
            {
                return BadRequest(new { error = "HTML content is required" });
            }
            
            if (request.Options == null)
            {
                return BadRequest(new { error = "Options are required" });
            }
            
            if (request.Options.Width <= 0 || request.Options.Height <= 0)
            {
                return BadRequest(new { error = "Width and height must be positive" });
            }
            
            if (request.Options.Format != "pdf")
            {
                return BadRequest(new { error = "Only PDF format is supported" });
            }
            
            // Render PDF - теперь синхронно
            byte[] pdfData = await Task.Run(() => _pdfRenderService.RenderPdf(request));
            
            _logger.LogInformation($"PDF successfully generated, size: {pdfData.Length} bytes");
            
            return File(pdfData, "application/pdf", $"document_{DateTime.Now:yyyyMMddHHmmss}.pdf");
        }
        catch (InvalidOperationException ex)
        {
            _logger.LogWarning(ex, "PDF contains more than one page");
            return BadRequest(new { error = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during PDF generation");
            return StatusCode(500, new {
                error = "Internal server error",
                details = ex.Message
            });
        }
    }

    [HttpPost("api/combine")]
    [Consumes("application/json")]
    [Produces("application/pdf")]
    public IActionResult Combine([FromBody] CombineRequest request)
    {
        if (request.PdfBase64 == null || request.PdfBase64.Count == 0)
        {
            return BadRequest(new { error = "No PDF data provided" });
        }

        try
        {
            var pdfBytes = request.PdfBase64.Select(b => Convert.FromBase64String(b));
            var combined = _pdfRenderService.CombinePdfs(pdfBytes);
            return File(combined, "application/pdf", $"combined_{DateTime.Now:yyyyMMddHHmmss}.pdf");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error combining PDFs");
            return StatusCode(500, new { error = ex.Message });
        }
    }
}

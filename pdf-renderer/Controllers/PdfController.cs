using System;
using System.IO;
using System.Threading.Tasks;
using System.Collections.Generic;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using PdfRenderer.Models;
using PdfRenderer.Services;

namespace PdfRenderer.Controllers
{
    [ApiController]
    [Route("api/pdf")]
    public class PdfController : ControllerBase
    {
        private readonly PdfRenderService _render;
        private readonly ValidationService _validation;
        private readonly PreviewService _preview;
        private readonly ILogger<PdfController> _logger;

        public PdfController(
            PdfRenderService render,
            ValidationService validation,
            PreviewService preview,
            ILogger<PdfController> logger)
        {
            _render = render;
            _validation = validation;
            _preview = preview;
            _logger = logger;
        }

        [HttpPost("render")]
        public async Task<IActionResult> RenderPdf([FromBody] PdfRequest request)
        {
            var validationResult = _validation.Validate(request);
            if (!validationResult.IsValid)
            {
                var errors = string.Join("; ", validationResult.Errors);
                _logger.LogError("Validation errors: {Errors}", errors);
                return BadRequest(new RenderResult { Error = errors });
            }

            try
            {
                _logger.LogInformation("Rendering PDF with dimensions: {Width}x{Height} {Units}, bleeds: {Bleeds}", 
                    request.Width, request.Height, request.Units, request.Bleeds);

                // Создаем список HTML-страниц (сейчас только одна)
                var htmlList = new List<string> { request.Html };
                
                // Создаем список базовых URI для разрешения ресурсов
                // В данном случае у нас нет базовых URI, так как HTML уже должен быть готов
                var uriList = new List<string> { string.Empty };

                // Рендерим PDF
                var pdfBytes = _render.RenderPdf(htmlList, uriList);
                
                // Результат операции
                var result = new RenderResult();

                // Если нужно превью, генерируем его
                if (request.GeneratePreview)
                {
                    _logger.LogInformation("Generating preview");
                    result.PreviewUrl = await _preview.GeneratePreviewAsync(pdfBytes);
                }
                
                // Возвращаем бинарные данные PDF
                return File(pdfBytes, "application/pdf");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error rendering PDF");
                return StatusCode(500, new RenderResult { Error = "Internal server error: " + ex.Message });
            }
        }
        
        [HttpGet("health")]
        public IActionResult HealthCheck()
        {
            return Ok(new { status = "ok", service = "pdf-renderer" });
        }
    }
}
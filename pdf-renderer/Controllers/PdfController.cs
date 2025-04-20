// Controllers/PdfController.cs
using Microsoft.AspNetCore.Mvc;
using FluentValidation;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using PdfRenderer.Models;
using PdfRenderer.Services;
using Microsoft.Extensions.Logging;

namespace PdfRenderer.Controllers;

[ApiController]
[Route("api/[controller]")]
public class PdfController : ControllerBase
{
    private readonly IValidator<PdfRequest> _validation;
    private readonly ILogger<PdfController> _logger;
    private readonly IPdfRenderService _render;
    private readonly IPreviewService _preview;

    public PdfController(
        IValidator<PdfRequest> validation,
        ILogger<PdfController> logger,
        IPdfRenderService render,
        IPreviewService preview)
    {
        _validation = validation;
        _logger = logger;
        _render = render;
        _preview = preview;
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
            var uriList = new List<string> { string.Empty };

            // Получаем настройки рендеринга из запроса
            var renderSettings = new Dictionary<string, string>();
            if (request.Settings != null)
            {
                renderSettings = request.Settings;
                _logger.LogInformation("Using render settings: {Settings}", 
                    string.Join(", ", request.Settings.Select(kvp => $"{kvp.Key}={kvp.Value}")));
            }

            // Рендерим PDF с настройками
            var pdfBytes = _render.RenderPdf(htmlList, uriList, renderSettings);
            
            // Результат операции
            var result = new RenderResult();

            // Если нужно превью, генерируем его
            if (request.GeneratePreview)
            {
                _logger.LogInformation("Generating preview");
                result.PreviewUrl = await _preview.GeneratePreviewAsync(pdfBytes);
            }
            
            // Возвращаем бинарные данные PDF с правильными заголовками
            var fileName = $"document-{DateTime.UtcNow:yyyyMMdd-HHmmss}.pdf";
            return File(pdfBytes, "application/pdf", fileName);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error rendering PDF");
            return StatusCode(500, new RenderResult { Error = "Internal server error: " + ex.Message });
        }
    }
}
using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.IO;
using System.Diagnostics;
using System.Threading.Tasks;
using PdfRenderer.Services;
using PdfRenderer.Models;
using PdfRenderer.Utils;
using iText.StyledXmlParser.Css.Validate.Impl;
using iText.StyledXmlParser.Css.Validate;
using Microsoft.Extensions.Logging;

namespace PdfRenderer.Controllers;

[ApiController]
[Route("api/pdf")]
public class PdfController : ControllerBase
{
    private readonly ILogger<PdfController> _logger;
    private readonly IPdfRenderService _pdfRenderService;
    private readonly IPreviewService _previewService;

    public PdfController(
        ILogger<PdfController> logger,
        IPdfRenderService pdfRenderService,
        IPreviewService previewService)
    {
        _logger = logger;
        _pdfRenderService = pdfRenderService;
        _previewService = previewService;
    }

    [HttpGet("health")]
    public IActionResult HealthCheck()
    {
        return Ok(new { status = "ok", service = "pdf-renderer" });
    }

    [HttpPost("render")]
    public async Task<IActionResult> Render([FromBody] PdfRequest request)
    {
        // Засекаем время для оценки производительности
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            _logger.LogInformation("Получен запрос на рендеринг PDF");
            
            // Валидация запроса - упрощенная
            if (string.IsNullOrWhiteSpace(request.Html))
            {
                return BadRequest(new { error = "HTML-содержимое обязательно" });
            }
            
            if (request.Width <= 0 || request.Height <= 0)
            {
                return BadRequest(new { error = "Ширина и высота должны быть положительными" });
            }
            
            // Конвертация размеров в пункты
            float width = UnitConverter.ConvertToPoints(request.Width, request.Units);
            float height = UnitConverter.ConvertToPoints(request.Height, request.Units);
            _logger.LogInformation($"Размеры страницы: {request.Width}x{request.Height} {request.Units} -> {width}x{height} pt");
            
            // Рендеринг PDF
            byte[] pdfData = _pdfRenderService.RenderPdf(
                new List<string> { request.Html }, 
                new List<string> { Directory.GetCurrentDirectory() },
                request.Settings ?? new Dictionary<string, string>()
            );
            
            // Генерация превью если требуется
            string? previewUrl = null;
            if (request.GeneratePreview)
            {
                previewUrl = await _previewService.GeneratePreviewAsync(pdfData);
                _logger.LogInformation($"Сгенерировано превью: {previewUrl}");
            }
            
            // Логирование результата
            stopwatch.Stop();
            _logger.LogInformation($"PDF успешно сгенерирован за {stopwatch.ElapsedMilliseconds} мс, размер: {pdfData.Length} байт");
            
            // Возвращаем PDF или информацию о превью
            if (!string.IsNullOrEmpty(previewUrl))
            {
                return Ok(new { previewUrl });
            }
            else
            {
                return File(pdfData, "application/pdf", $"document_{DateTime.Now:yyyyMMddHHmmss}.pdf");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Ошибка при генерации PDF");
            return StatusCode(500, new { error = "Внутренняя ошибка сервера", details = ex.Message });
        }
    }
}
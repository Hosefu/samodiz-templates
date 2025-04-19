using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Configuration;
using PdfGenerator.Models;
using PdfGenerator.Services;

namespace PdfGenerator.Controllers
{
    [ApiController]
    [Route("api/pdf")]
    public class PdfController : ControllerBase
    {
        private readonly TemplateCacheService _cache;
        private readonly PdfRenderService _render;
        private readonly RazorTemplateService _razor;
        private readonly ValidationService _validation;
        private readonly PreviewService _preview;
        private readonly ILogger<PdfController> _logger;
        private readonly IHostEnvironment _env;
        private readonly IConfiguration _configuration;

        public PdfController(
            TemplateCacheService cache,
            PdfRenderService render,
            RazorTemplateService razor,
            ValidationService validation,
            PreviewService preview,
            ILogger<PdfController> logger,
            IHostEnvironment env,
            IConfiguration configuration)
        {
            _cache = cache;
            _render = render;
            _razor = razor;
            _validation = validation;
            _preview = preview;
            _logger = logger;
            _env = env;
            _configuration = configuration;
        }

        [HttpPost("generate")]
        public async Task<IActionResult> GeneratePdf([FromBody] PdfRequest request)
        {
            var validationResult = _validation.Validate(request);
            if (!validationResult.IsValid)
            {
                var errors = string.Join("; ", validationResult.Errors.Select(e => e.ErrorMessage));
                return BadRequest(new RenderResult { Error = errors });
            }

            try
            {
                var template = await _cache.GetTemplateAsync(request.TemplateId);

                // кэш-папка берётся из вашего TemplateCacheService (добавьте публичное свойство CacheRoot)
                var cacheRoot = _cache.CacheRoot; 
                var tplId     = request.TemplateId;

                var pages = template.Pages
                    .Select(p => new {
                        Html    = _razor.RenderPage(p, request.Data),
                        BaseUri = Path.Combine(cacheRoot, tplId.ToString(), p.Name)
                    })
                    .ToList();

                var htmlList = pages.Select(x => x.Html).ToList();
                var uriList  = pages.Select(x => x.BaseUri).ToList();

                var pdfBytes = _render.RenderPdf(htmlList, uriList);

                var pdfPath = await SaveFileAsync(pdfBytes, "pdf", request.TemplateId, request.Data);
                string previewPath = string.Empty;

                if (request.GeneratePreview)
                {
                    previewPath = await _preview.GeneratePreviewAsync(pdfBytes);
                }

                return Ok(new RenderResult
                {
                    PdfPath = pdfPath,
                    PreviewPath = previewPath
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "PDF generation failed");
                return StatusCode(500, new RenderResult { Error = "Internal server error" });
            }
        }

        private async Task<string> SaveFileAsync(byte[] content, string ext, int templateId, Dictionary<string, string> formData)
        {
            var fileName = $"{Guid.NewGuid()}.{ext}";
            
            // Создаем форму для отправки
            using var form = new MultipartFormDataContent();
            
            // Добавляем файл PDF
            using var fileContent = new ByteArrayContent(content);
            form.Add(fileContent, "file", fileName);
            
            // Добавляем ID шаблона
            form.Add(new StringContent(templateId.ToString()), "template_id");
            
            // Добавляем данные в формате JSON
            if (formData != null)
            {
                var formDataJson = JsonSerializer.Serialize(formData);
                form.Add(new StringContent(formDataJson), "form_data");
            }
            
            // Настраиваем HTTP клиент с API-ключом
            using var httpClient = new HttpClient();
            var apiKey = _configuration["ApiKey"];
            _logger.LogInformation($"Using API key: {apiKey}");
            
            if (!string.IsNullOrEmpty(apiKey))
            {
                httpClient.DefaultRequestHeaders.Add("X-API-Key", apiKey);
            }
            
            var uploadUrl = "http://storage:8000/api/upload-pdf/";
            _logger.LogInformation($"Uploading PDF to: {uploadUrl}");
            
            // Отправляем запрос
            var response = await httpClient.PostAsync(uploadUrl, form);
            
            // Всегда логируем статус ответа
            _logger.LogInformation($"Upload response status: {response.StatusCode}");
            
            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError($"Ошибка загрузки PDF: {response.StatusCode}, Error: {errorContent}");
                throw new Exception($"Ошибка загрузки PDF: {response.StatusCode}");
            }
            
            // Читаем JSON-ответ и логируем его для отладки
            var jsonString = await response.Content.ReadAsStringAsync();
            _logger.LogInformation($"API response: {jsonString}");

            try {
                // Используем JsonDocument для получения URL, который всегда строка
                using var jsonDoc = JsonDocument.Parse(jsonString);
                if (jsonDoc.RootElement.TryGetProperty("url", out var urlElement)) {
                    var url = urlElement.GetString() ?? "/error";
                    _logger.LogInformation($"PDF URL: {url}");
                    return url;
                }
                else {
                    _logger.LogError("URL не найден в ответе API");
                    return "/error";
                }
            }
            catch (JsonException ex) {
                _logger.LogError(ex, "Ошибка разбора JSON");
                return "/error";
            }
        }
    }
}
using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Collections.Generic;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Hosting;
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

        public PdfController(
            TemplateCacheService cache,
            PdfRenderService render,
            RazorTemplateService razor,
            ValidationService validation,
            PreviewService preview,
            ILogger<PdfController> logger,
            IHostEnvironment env)
        {
            _cache = cache;
            _render = render;
            _razor = razor;
            _validation = validation;
            _preview = preview;
            _logger = logger;
            _env = env;
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


                var pdfPath = await SaveFileAsync(pdfBytes, "pdf");
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

        private async Task<string> SaveFileAsync(byte[] content, string ext)
        {
            var fileName = $"{Guid.NewGuid()}.{ext}";
            var webRoot = Path.Combine(_env.ContentRootPath, "wwwroot");
            Directory.CreateDirectory(webRoot);
            var path = Path.Combine(webRoot, fileName);
            await System.IO.File.WriteAllBytesAsync(path, content);
            return $"/{fileName}";
        }
    }
}

using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Linq;
using iText.Html2pdf;
using iText.Html2pdf.Css;
using iText.Kernel.Pdf;
using iText.Kernel.Utils;
using iText.StyledXmlParser.Css.Validate;
using iText.StyledXmlParser.Css.Validate.Impl;
using iText.IO.Font;
using iText.IO.Font.Constants;
using iText.Html2pdf.Resolver.Font;
using Microsoft.Extensions.Logging;

namespace PdfRenderer.Services
{
    public class PdfRenderService : IPdfRenderService
    {
        private readonly ILogger<PdfRenderService> _logger;

        public PdfRenderService(ILogger<PdfRenderService> logger) 
            => _logger = logger;

        /// <summary>
        /// Рендерит HTML в PDF
        /// </summary>
        /// <param name="htmlPages">Список HTML-строк для рендеринга</param>
        /// <param name="baseUris">Список базовых путей для ресурсов, по одному на каждую страницу</param>
        /// <param name="settings">Дополнительные настройки рендеринга</param>
        /// <returns>PDF-документ в виде массива байтов</returns>
        public byte[] RenderPdf(
            List<string> htmlPages,
            List<string> baseUris,
            Dictionary<string, string>? settings = null)
        {
            // Проверить, что количество HTML-страниц и baseUris совпадает
            if (htmlPages.Count != baseUris.Count)
                throw new ArgumentException("htmlPages и baseUris должны быть одинаковой длины");

            // Настроить валидатор CSS
            CssDeclarationValidationMaster.SetValidator(new CssDeviceCmykAwareValidator());

            // Если всего одна страница, используем прямое преобразование
            if (htmlPages.Count == 1)
            {
                _logger.LogInformation("Рендеринг одностраничного PDF");
                using var ms = new MemoryStream();
                var props = CreateConverterProperties(baseUris[0]);
                
                using var htmlStream = new MemoryStream(Encoding.UTF8.GetBytes(htmlPages[0]));
                HtmlConverter.ConvertToPdf(htmlStream, ms, props);
                
                return ms.ToArray();
            }
            
            // Для нескольких страниц - создаем каждую отдельно и объединяем
            _logger.LogInformation($"Рендеринг многостраничного PDF ({htmlPages.Count} страниц)");
            List<byte[]> pdfPages = new List<byte[]>();
            
            // Создаем отдельный PDF для каждой страницы
            for (int i = 0; i < htmlPages.Count; i++)
            {
                string html = htmlPages[i];
                string baseUri = baseUris[i];
                
                var props = CreateConverterProperties(baseUri);
                
                using (MemoryStream pageMs = new MemoryStream())
                {
                    using (MemoryStream htmlStream = new MemoryStream(Encoding.UTF8.GetBytes(html)))
                    {
                        HtmlConverter.ConvertToPdf(htmlStream, pageMs, props);
                    }
                    
                    pdfPages.Add(pageMs.ToArray());
                }
            }
            
            // Если в итоге получилась только одна страница
            if (pdfPages.Count == 1)
            {
                return pdfPages[0];
            }
            
            // Объединяем все PDF в один документ
            using MemoryStream resultMs = new MemoryStream();
            using PdfWriter writer = new PdfWriter(resultMs);
            using PdfDocument resultDoc = new PdfDocument(writer);
            PdfMerger merger = new PdfMerger(resultDoc);
            
            foreach (byte[] pdfBytes in pdfPages)
            {
                using MemoryStream srcMs = new MemoryStream(pdfBytes);
                using PdfReader reader = new PdfReader(srcMs);
                using PdfDocument srcDoc = new PdfDocument(reader);
                
                merger.Merge(srcDoc, 1, srcDoc.GetNumberOfPages());
            }
            
            resultDoc.Close();
            
            return resultMs.ToArray();
        }
        
        /// <summary>
        /// Создаёт настройки для конвертации с поддержкой шрифтов
        /// </summary>
        private ConverterProperties CreateConverterProperties(string baseUri)
        {
            var props = new ConverterProperties();
            props.SetBaseUri(baseUri);
            
            // Создаем провайдер шрифтов
            #pragma warning disable 612, 618
            var fontProvider = new DefaultFontProvider(false, false, false);
            #pragma warning restore 612, 618
            
            // Проверяем наличие шрифтов в директории assets
            var assetsDir = Path.Combine(baseUri, "assets");
            if (Directory.Exists(assetsDir))
            {
                var fontFiles = Directory.GetFiles(assetsDir, "*.ttf")
                    .Concat(Directory.GetFiles(assetsDir, "*.otf"))
                    .ToList();
                
                if (fontFiles.Any())
                {
                    _logger.LogInformation($"Найдено {fontFiles.Count} шрифтов в {assetsDir}");
                    fontProvider.AddDirectory(assetsDir);
                }
                else
                {
                    // Если шрифты не найдены, используем стандартные
                    #pragma warning disable 612, 618
                    fontProvider = new DefaultFontProvider(true, false, false);
                    #pragma warning restore 612, 618
                }
            }
            else
            {
                // Если директория assets не найдена, используем стандартные шрифты
                #pragma warning disable 612, 618
                fontProvider = new DefaultFontProvider(true, false, false);
                #pragma warning restore 612, 618
            }
            
            props.SetFontProvider(fontProvider);
            return props;
        }
    }
}
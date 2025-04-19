using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Linq;
using iText.Html2pdf;
using iText.Html2pdf.Css;                             // для CssDeclarationValidationMaster
using iText.Kernel.Pdf;
using iText.Kernel.Utils;                             // для PdfMerger
using iText.StyledXmlParser.Css.Validate;              // для интерфейса валидатора
using iText.StyledXmlParser.Css.Validate.Impl;         // для CssDeviceCmykAwareValidator
using iText.IO.Font;                                   // для шрифтового провайдера
using iText.IO.Font.Constants;
using iText.Html2pdf.Resolver.Font;  
using Microsoft.Extensions.Logging;

namespace PdfGenerator.Services
{
    public class PdfRenderService
    {
        private readonly ILogger<PdfRenderService> _logger;

        public PdfRenderService(ILogger<PdfRenderService> logger) 
            => _logger = logger;

        /// <summary>
        /// pagesHtml — список html-строк  
        /// baseUris  — список папок, откуда брать assets (fonts, картинки) для каждой страницы
        /// </summary>
        public byte[] RenderPdf(
            List<string> pagesHtml,
            List<string> baseUris)
        {
            if (pagesHtml.Count != baseUris.Count)
                throw new ArgumentException("pagesHtml и baseUris должны быть одинаковой длины");

            // 1) поставить валидатор, чтобы device-cmyk() распознавался
            CssDeclarationValidationMaster.SetValidator(new CssDeviceCmykAwareValidator());

            // Если всего одна страница, обрабатываем её напрямую
            if (pagesHtml.Count == 1)
            {
                using var ms = new MemoryStream();
                
                var props = CreateConverterProperties(baseUris[0]);
                
                using var htmlStream = new MemoryStream(Encoding.UTF8.GetBytes(pagesHtml[0]));
                HtmlConverter.ConvertToPdf(htmlStream, ms, props);
                
                return ms.ToArray();
            }
            
            // Для нескольких страниц - создаем отдельные PDF и объединяем
            List<byte[]> pdfPages = new List<byte[]>();
            
            // Создаем отдельный PDF для каждой страницы
            for (int i = 0; i < pagesHtml.Count; i++)
            {
                _logger.LogInformation($"Обработка страницы {i+1} из {pagesHtml.Count}");
                
                string html = pagesHtml[i];
                string baseUri = baseUris[i];
                
                var props = CreateConverterProperties(baseUri);
                
                // Создаем отдельный поток для каждой страницы
                using (MemoryStream pageMs = new MemoryStream())
                {
                    using (MemoryStream htmlStream = new MemoryStream(Encoding.UTF8.GetBytes(html)))
                    {
                        HtmlConverter.ConvertToPdf(htmlStream, pageMs, props);
                    }
                    
                    // Сохраняем полученный PDF в массив байтов
                    var pdfBytes = pageMs.ToArray();
                    pdfPages.Add(pdfBytes);
                    
                    _logger.LogInformation($"Страница {i+1} успешно сконвертирована, размер: {pdfBytes.Length} байт");
                }
            }
            
            // Если в итоге получилась только одна страница
            if (pdfPages.Count == 1)
            {
                return pdfPages[0];
            }
            
            // Объединяем все PDF в один документ
            _logger.LogInformation("Объединение страниц в итоговый PDF");
            
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
            
            resultDoc.Close(); // Важно закрыть документ перед получением данных
            
            byte[] finalPdf = resultMs.ToArray();
            _logger.LogInformation($"Итоговый PDF создан, размер: {finalPdf.Length} байт");
            
            return finalPdf;
        }
        
        /// <summary>
        /// Создаёт и настраивает ConverterProperties с нужными параметрами и гарантирует наличие шрифтов
        /// </summary>
        private ConverterProperties CreateConverterProperties(string baseUri)
        {
            var props = new ConverterProperties();
            props.SetBaseUri(baseUri);
            
            // Создаем наш провайдер шрифтов
            #pragma warning disable 612, 618
            var fontProvider = new DefaultFontProvider(false, false, false);
            #pragma warning restore 612, 618
            
            bool hasAddedFonts = false;
            
            // Проверяем наличие и добавляем шрифты из директории assets
            var assetsDir = Path.Combine(baseUri, "assets");
            if (Directory.Exists(assetsDir))
            {
                var fontFiles = Directory.GetFiles(assetsDir, "*.ttf")
                    .Concat(Directory.GetFiles(assetsDir, "*.otf"))
                    .ToList();
                
                if (fontFiles.Any())
                {
                    _logger.LogInformation($"Добавление шрифтов из {assetsDir} ({fontFiles.Count} файлов)");
                    fontProvider.AddDirectory(assetsDir);
                    hasAddedFonts = true;
                }
                else
                {
                    _logger.LogInformation($"Директория {assetsDir} существует, но не содержит шрифтов .ttf или .otf");
                }
            }
            else
            {
                _logger.LogInformation($"Директория с шрифтами не найдена: {assetsDir}");
            }
            
            // Если не нашли никаких пользовательских шрифтов, включаем стандартные шрифты
            if (!hasAddedFonts)
            {
                _logger.LogInformation("Пользовательские шрифты не найдены, используем стандартные шрифты");
                
                // Создаем новый провайдер со стандартными шрифтами
                #pragma warning disable 612, 618
                fontProvider = new DefaultFontProvider(true, false, false);
                #pragma warning restore 612, 618
            }
            
            props.SetFontProvider(fontProvider);
            return props;
        }
    }
}
using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using iText.Html2pdf;
using iText.Html2pdf.Css;                             // для CssDeclarationValidationMaster
using iText.Kernel.Pdf;
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

            using var ms = new MemoryStream();
            using var writer = new PdfWriter(ms);
            using var pdf   = new PdfDocument(writer);

            for (int i = 0; i < pagesHtml.Count; i++)
            {
                var html    = pagesHtml[i];
                var baseUri = baseUris[i];

                // 2) каждая страница — свои ConverterProperties
                var props = new ConverterProperties();

                // указываем, где корень относительно HTML (для url('assets/...'))
                props.SetBaseUri(baseUri);

                // 3) шрифтовый провайдер: подхватит ваши TTF из assets
                var fontProvider = new DefaultFontProvider(false, false, false);
                var assetsDir    = Path.Combine(baseUri, "assets");
                if (Directory.Exists(assetsDir))
                    fontProvider.AddDirectory(assetsDir);
                props.SetFontProvider(fontProvider);

                // Конвертим HTML в PDF
                using var htmlStream = new MemoryStream(Encoding.UTF8.GetBytes(html));
                HtmlConverter.ConvertToPdf(htmlStream, pdf, props);

                // Разделитель страниц
                if (i < pagesHtml.Count - 1)
                    pdf.AddNewPage();
            }

            return ms.ToArray();
        }
    }
}

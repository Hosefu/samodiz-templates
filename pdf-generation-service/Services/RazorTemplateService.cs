using System.Collections.Generic;
using PdfGenerator.Models;

namespace PdfGenerator.Services
{
    public class RazorTemplateService
    {
        /// <summary>
        /// Рендерит страницу, подставляя в HTML значения из словаря.
        /// </summary>
        public string RenderPage(TemplateMeta.TemplatePage page, Dictionary<string, string> data)
        {
            // Берём исходный HTML-шаблон
            var html = page.Html;

            // Для каждого поля шаблона делаем Replace {{FieldName}} -> value
            foreach (var field in page.Fields)
            {
                var placeholder = $"{{{{{field.Name}}}}}";
                var value = data.GetValueOrDefault(field.Name) ?? string.Empty;
                html = html.Replace(placeholder, value);
            }

            return html;
        }
    }
}

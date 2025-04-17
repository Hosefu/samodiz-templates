using System.Collections.Generic;

namespace PdfGenerator.Models;

public class PdfRequest
{
    /// <summary>ID запрашиваемого шаблона из API</summary>
    public int TemplateId { get; set; }
    
    /// <summary>Данные для подстановки в шаблон</summary>
    /// <example>{{"last_name": "Иванов", "position": "Директор"}}</example>
    public required Dictionary<string, string> Data { get; set; }
    
    /// <summary>Генерировать ли PNG-превью</summary>
    public bool GeneratePreview { get; set; }
}
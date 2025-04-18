using System.Collections.Generic;

namespace PdfGenerator.Models;

public class TemplateMeta
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Version { get; set; } = string.Empty;
    public List<TemplatePage> Pages { get; set; } = new();

    public class TemplatePage
    {
        public string Name { get; set; } = string.Empty;
        public string Html { get; set; } = string.Empty;
        public int Width { get; set; } 
        public int Height { get; set; }
        public int Bleeds { get; set; }
        public List<TemplateField> Fields { get; set; } = new();
        public List<PageAsset> Assets { get; set; } = new();
    }

    public class TemplateField
    {
        public string Name { get; set; } = string.Empty;
        public bool Required { get; set; }
    }

    public class PageAsset
    {
        public string File { get; set; } = string.Empty;
    }
}
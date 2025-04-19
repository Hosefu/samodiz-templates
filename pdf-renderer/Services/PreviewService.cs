using ImageMagick;
using System;
using System.IO;
using System.Threading.Tasks;

namespace PdfGenerator.Services
{
    public class PreviewService
    {
        public async Task<string> GeneratePreviewAsync(byte[] pdfBytes)
        {
            // Настройки для чтения PDF с нужным DPI
            var settings = new MagickReadSettings
            {
                Format = MagickFormat.Pdf,
                Density = new Density(150)
            };

            using var images = new MagickImageCollection();
            using var ms = new MemoryStream(pdfBytes);
            images.Read(ms, settings);  // читаем из потока с настройками

            // Берём первую страницу
            var image = images[0];
            image.Format = MagickFormat.Png;
            image.Quality = 90;

            // Готовим wwwroot
            var wwwroot = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot");
            Directory.CreateDirectory(wwwroot);

            var fileName = $"{Guid.NewGuid()}.png";
            var filePath = Path.Combine(wwwroot, fileName);
            await image.WriteAsync(filePath);

            return $"/{fileName}";
        }
    }
}

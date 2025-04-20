using System;
using System.IO;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using PdfGenerator.Models;

namespace PdfGenerator.Services
{
    public class TemplateCacheService
    {
        private readonly HttpClient _httpClient;
        private readonly string _cacheRoot;
        private readonly ILogger<TemplateCacheService> _logger;

        public TemplateCacheService(
            HttpClient httpClient,
            IConfiguration config,
            ILogger<TemplateCacheService> logger)
        {
            _httpClient = httpClient;
            _logger = logger;

            var cachePath = config["Cache:Path"] ?? "Cache";
            _cacheRoot = Path.Combine(cachePath, "templates");
            Directory.CreateDirectory(_cacheRoot);
            _logger.LogInformation($"Cache directory: {_cacheRoot}");
        }

        public async Task<TemplateMeta> GetTemplateAsync(int templateId)
        {
            var templateDir = Path.Combine(_cacheRoot, templateId.ToString());
            var metaFile = Path.Combine(templateDir, "template.json");
            
            // Сначала проверяем актуальность версии шаблона в API
            bool needUpdate = true;
            string currentVersion = "";
            
            try 
            {
                // Получаем текущую версию из API
                _logger.LogInformation("Checking template {id} version from API", templateId);
                var response = await _httpClient.GetAsync($"api/templates/{templateId}");
                response.EnsureSuccessStatusCode();
                
                var apiTemplate = await response.Content.ReadFromJsonAsync<TemplateMeta>();
                if (apiTemplate == null) 
                {
                    throw new InvalidOperationException("Invalid template response");
                }
                
                currentVersion = apiTemplate.Version;
                _logger.LogInformation("API template version: {version}", currentVersion);
                
                // Если есть кэшированный шаблон, проверяем его версию
                if (File.Exists(metaFile))
                {
                    var cachedTemplate = LoadCachedTemplate(metaFile);
                    _logger.LogInformation("Cached template version: {version}", cachedTemplate.Version);
                    
                    // Если версии совпадают, обновление не требуется
                    if (cachedTemplate.Version == currentVersion)
                    {
                        _logger.LogInformation("Template version matches cache, using cached version");
                        needUpdate = false;
                        return cachedTemplate;
                    }
                    else
                    {
                        _logger.LogInformation("Template version mismatch: API={apiVersion}, Cache={cacheVersion}",
                            currentVersion, cachedTemplate.Version);
                    }
                }
                
                // Если файла нет или версии не совпадают, обновляем кэш
                if (needUpdate)
                {
                    _logger.LogInformation("Updating template {id} in cache...", templateId);
                    await CacheTemplateFromApiAsync(templateId, templateDir, apiTemplate);
                    return apiTemplate;
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error checking template version. Trying to use cached version if available.");
                
                // Если API недоступен, но есть кэш - используем его
                if (File.Exists(metaFile))
                {
                    _logger.LogWarning("Using cached template as fallback");
                    return LoadCachedTemplate(metaFile);
                }
                
                // Если нет доступа к API и кэша нет - пробуем еще раз получить шаблон
                _logger.LogInformation("Trying to cache template {id}...", templateId);
                await CacheTemplateFromApiAsync(templateId, templateDir);
            }
            
            return LoadCachedTemplate(metaFile);
        }

        private async Task CacheTemplateFromApiAsync(int templateId, string templateDir, TemplateMeta? template = null)
        {
            try
            {
                // Если шаблон не передан, загружаем его из API
                if (template == null)
                {
                    _logger.LogInformation("Загрузка шаблона {id} из {url}", templateId, _httpClient.BaseAddress);

                    var response = await _httpClient.GetAsync($"api/templates/{templateId}");
                    response.EnsureSuccessStatusCode();

                    var jsonResponse = await response.Content.ReadAsStringAsync();
                    _logger.LogInformation("API Response: {response}", jsonResponse.Substring(0, Math.Min(jsonResponse.Length, 100)));

                    template = await response.Content.ReadFromJsonAsync<TemplateMeta>()
                        ?? throw new InvalidOperationException("Invalid template response");
                }

                // Очищаем существующую директорию шаблона, если она есть
                if (Directory.Exists(templateDir))
                {
                    _logger.LogInformation("Cleaning existing template directory: {dir}", templateDir);
                    Directory.Delete(templateDir, true);
                }

                Directory.CreateDirectory(templateDir);
                var metaJson = JsonSerializer.Serialize(template, new JsonSerializerOptions { WriteIndented = true });
                var metaPath = Path.Combine(templateDir, "template.json");
                await File.WriteAllTextAsync(metaPath, metaJson);

                foreach (var page in template.Pages)
                {
                    var pageDir = Path.Combine(templateDir, page.Name);
                    var assetsDir = Path.Combine(pageDir, "assets");
                    Directory.CreateDirectory(assetsDir);

                    foreach (var asset in page.Assets)
                    {
                        _logger.LogInformation("↘ Downloading asset {url}", asset.File);
                        
                        // Корректируем URL-адрес, убираем первый слэш если он есть
                        string assetUrl = asset.File;
                        if (assetUrl.StartsWith("/"))
                            assetUrl = assetUrl.Substring(1);
                        
                        var bytes = await _httpClient.GetByteArrayAsync(assetUrl);
                        _logger.LogInformation("  ↳ {size} bytes downloaded", bytes.Length);

                        var fileName = Path.GetFileName(new Uri(asset.File).LocalPath);
                        var assetPath = Path.Combine(assetsDir, fileName);
                        await File.WriteAllBytesAsync(assetPath, bytes);

                        _logger.LogInformation("  ↳ Saved to {path}", assetPath);
                    }

                    var htmlPath = Path.Combine(pageDir, $"{page.Name}.html");
                    await File.WriteAllTextAsync(htmlPath, page.Html);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error caching template {templateId}");
                throw;
            }
        }

        private TemplateMeta LoadCachedTemplate(string metaFile)
        {
            var json = File.ReadAllText(metaFile);
            return JsonSerializer.Deserialize<TemplateMeta>(json)
                   ?? throw new InvalidOperationException("Failed to deserialize template metadata");
        }

        public string CacheRoot => _cacheRoot;
    }
}
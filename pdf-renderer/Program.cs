using System;
using System.IO;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using PdfRenderer.Services;
using PdfRenderer.Models;
using FluentValidation;

var builder = WebApplication.CreateBuilder(args);

// Добавляем контроллеры
builder.Services.AddControllers();

// Настраиваем сервисы
builder.Services.AddTransient<IPdfRenderService, PdfRenderService>();
builder.Services.AddTransient<ValidationService>();
builder.Services.AddTransient<IPreviewService, PreviewService>();

// Регистрируем валидатор
builder.Services.AddTransient<IValidator<PdfRequest>, PdfRequestValidator>();

// Добавляем конфигурацию в контейнер служб
builder.Services.AddSingleton(builder.Configuration);

// Настраиваем HttpClient для TemplateCacheService
builder.Services.AddHttpClient<TemplateCacheService>(client =>
{
    client.BaseAddress = new Uri(builder.Configuration["StorageBaseUrl"] ?? "http://storage-service:8000/");
    if (!string.IsNullOrEmpty(builder.Configuration["ApiKey"]))
    {
        client.DefaultRequestHeaders.Add("X-API-Key", builder.Configuration["ApiKey"]);
    }
});

// Регистрируем TemplateCacheService как Singleton
builder.Services.AddSingleton<TemplateCacheService>();

// Настраиваем CORS
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// Настраиваем логирование
builder.Logging.ClearProviders();
builder.Logging.AddConsole();
builder.Logging.AddDebug();

var app = builder.Build();

// Создаем каталог для wwwroot, если он не существует
var wwwroot = Path.Combine(app.Environment.ContentRootPath, "wwwroot");
Directory.CreateDirectory(wwwroot);

// Настраиваем конвейер HTTP-запросов
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}

app.UseRouting();
app.UseCors();
app.UseAuthorization();
app.MapControllers();

app.Run();
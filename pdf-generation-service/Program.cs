using System;
using System.IO;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using PdfGenerator.Services;

var builder = WebApplication.CreateBuilder(args);

// 0) Настройка CORS, чтобы фронт http://localhost:3000 мог стучаться
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowReactDev", policy =>
    {
        policy
          .WithOrigins("http://localhost:3000")  // адрес вашего React
          .AllowAnyHeader()
          .AllowAnyMethod();
    });
});

// 1) HTTP-клиент для TemplateCacheService (без .AddSingleton)
builder.Services.AddHttpClient<TemplateCacheService>(client =>
{
    var baseUrl = builder.Configuration["TemplateApi:BaseUrl"]!;
    client.BaseAddress = new Uri(baseUrl);
});

// 2) Остальные сервисы
builder.Services.AddControllers();
builder.Services.AddTransient<PdfRenderService>();
builder.Services.AddTransient<RazorTemplateService>();
builder.Services.AddTransient<ValidationService>();
builder.Services.AddTransient<PreviewService>();

var app = builder.Build();

// 3) Включаем CORS-политику
app.UseCors("AllowReactDev");

// 4) Создаём wwwroot
var wwwroot = Path.Combine(app.Environment.ContentRootPath, "wwwroot");
Directory.CreateDirectory(wwwroot);

// 5) Маршруты
app.MapControllers();

app.Run();

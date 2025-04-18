using System;
using System.IO;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using PdfGenerator.Services;

var builder = WebApplication.CreateBuilder(args);

// Только _этот_ вызов — без AddSingleton!
builder.Services.AddHttpClient<TemplateCacheService>(client =>
{
    var baseUrl = builder.Configuration["TemplateApi:BaseUrl"]!;
    client.BaseAddress = new Uri(baseUrl);
});

builder.Services.AddControllers();
// builder.Services.AddSingleton<TemplateCacheService>();  <- удалили
builder.Services.AddTransient<PdfRenderService>();
builder.Services.AddTransient<RazorTemplateService>();
builder.Services.AddTransient<ValidationService>();
builder.Services.AddTransient<PreviewService>();

var app = builder.Build();

var wwwroot = Path.Combine(app.Environment.ContentRootPath, "wwwroot");
Directory.CreateDirectory(wwwroot);

app.MapControllers();
app.Run();

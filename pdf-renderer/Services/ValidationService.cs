using PdfRenderer.Models;
using FluentValidation;
using FluentValidation.Results;

namespace PdfRenderer.Services;

/// <summary>
/// Сервис для валидации запросов
/// </summary>
public class ValidationService
{
    private readonly IValidator<PdfRequest> _validator;

    public ValidationService(IValidator<PdfRequest> validator)
    {
        _validator = validator;
    }

    /// <summary>
    /// Проверяет запрос на рендеринг PDF
    /// </summary>
    public ValidationResult Validate(PdfRequest request)
    {
        return _validator.Validate(request);
    }
}
using PdfRenderer.Models;
using FluentValidation;
using FluentValidation.Results;

namespace PdfRenderer.Services;

/// <summary>
/// Сервис для валидации запросов
/// </summary>
public class ValidationService
{
    /// <summary>
    /// Проверяет запрос на рендеринг PDF
    /// </summary>
    public ValidationResult Validate(PdfRequest request)
    {
        var validator = new PdfRequestValidator();
        return validator.Validate(request);
    }

    /// <summary>
    /// Валидатор для запросов на рендеринг PDF
    /// </summary>
    private class PdfRequestValidator : AbstractValidator<PdfRequest>
    {
        public PdfRequestValidator()
        {
            RuleFor(x => x.Html).NotEmpty().WithMessage("HTML content is required");
            RuleFor(x => x.Width).GreaterThan(0).WithMessage("Width must be positive");
            RuleFor(x => x.Height).GreaterThan(0).WithMessage("Height must be positive");
            
            RuleFor(x => x.Units)
                .NotEmpty()
                .Must(units => units == "mm" || units == "px")
                .WithMessage("Units must be 'mm' or 'px'");
            
            // Bleeds могут быть нулевыми, но не отрицательными
            RuleFor(x => x.Bleeds).GreaterThanOrEqualTo(0).WithMessage("Bleeds cannot be negative");
        }
    }
}
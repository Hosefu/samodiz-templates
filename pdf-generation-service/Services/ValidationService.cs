using PdfGenerator.Models;
using FluentValidation;
using FluentValidation.Results;

namespace PdfGenerator.Services;

public class ValidationService
{
    public FluentValidation.Results.ValidationResult Validate(PdfRequest request)
    {
        var validator = new PdfRequestValidator();
        return validator.Validate(request);
    }

    private class PdfRequestValidator : AbstractValidator<PdfRequest>
    {
        public PdfRequestValidator()
        {
            RuleFor(x => x.TemplateId).NotEmpty();
            RuleFor(x => x.Data).NotEmpty();
        }
    }
}
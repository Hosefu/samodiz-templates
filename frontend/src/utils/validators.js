export const required = (value) => {
  if (!value || value.trim() === '') {
    return 'Это поле обязательно';
  }
  return null;
};

export const email = (value) => {
  if (!value) return null;
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(value)) {
    return 'Некорректный email адрес';
  }
  return null;
};

export const minLength = (min) => (value) => {
  if (!value) return null;
  
  if (value.length < min) {
    return `Минимальная длина - ${min} символов`;
  }
  return null;
};

export const validateForm = (values, validationRules) => {
  const errors = {};
  
  Object.keys(validationRules).forEach(key => {
    const rules = validationRules[key];
    
    for (const rule of rules) {
      const error = rule(values[key]);
      if (error) {
        errors[key] = error;
        break;
      }
    }
  });
  
  return errors;
}; 
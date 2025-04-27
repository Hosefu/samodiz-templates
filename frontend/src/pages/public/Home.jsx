import React from 'react';

// Временное упрощение для теста
const Home = () => {
  return (
    <div className="p-10 bg-yellow-100 border border-yellow-400">
      <h1 className="text-2xl font-bold">Тест компонента Home</h1>
      <p>Если вы видите этот текст, значит, Outlet в App.jsx работает, и проблема внутри исходной логики Home.jsx.</p>
    </div>
  );
};

export default Home;

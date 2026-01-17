import React from 'react';

const ChartPlaceholder = ({ title, height = 'h-64' }) => {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <div className={`${height} flex items-center justify-center bg-gray-50 rounded border-2 border-dashed border-gray-300`}>
        <p className="text-gray-500">[Chart: {title}]</p>
      </div>
    </div>
  );
};

export default ChartPlaceholder;

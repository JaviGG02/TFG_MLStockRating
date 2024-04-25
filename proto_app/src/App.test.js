import ResizeObserver from 'resize-observer-polyfill';
global.ResizeObserver = ResizeObserver;
import React from "react";
import { render, screen } from "@testing-library/react";
import PricePredictionChart from "./components/PricePredictionChart/PricePredictionChart";
import FinancialTable from "./components/FinancialTable/FinancialTable";

describe("PricePredictionChart", () => {
  const mockDatosFinancieros = {
    TIME_SERIES_MONTHLY_ADJUSTED: {
      "2021-01-01": 100,
      "2021-02-01": 105,
    }
  };

  const mockPredicciones = {
    "2021-03-01": 110,
    "2021-04-01": 115,
  };

  test("muestra 'Cargando datos...' cuando no se proporcionan datos", () => {
    render(<PricePredictionChart />);
    expect(screen.getByText(/cargando datos.../i)).toBeInTheDocument();
  });

  test("renderiza el gráfico cuando se proporcionan datos", () => {
    render(
      <PricePredictionChart 
        datosFinancieros={mockDatosFinancieros} 
        predicciones={mockPredicciones} 
      />
    );
    // Se displayean las leyendas, por tanto el grafico tambien
    expect(screen.getByText(/PrecioReal/i)).toBeInTheDocument();
    expect(screen.getByText(/Predicción/i)).toBeInTheDocument();
  });
});

describe("FinancialTable", () => {
  test("renders financial data correctly", () => {
    const mockData = {
      incomeStatement: [{ fiscalDateEnding: "2021", totalRevenue: "5000" }],
      balanceSheet: [{ fiscalDateEnding: "2021", totalAssets: "10000" }],
      cashFlows: [{ fiscalDateEnding: "2021", operatingCashflow: "2000" }],
    };
    render(<FinancialTable {...mockData} />);
    expect(screen.getByText(/total revenue/i)).toBeInTheDocument();
    expect(screen.getByText(/5000/i)).toBeInTheDocument();
    expect(screen.getByText(/total assets/i)).toBeInTheDocument();
    expect(screen.getByText(/10000/i)).toBeInTheDocument();
    expect(screen.getByText(/operating cash flow/i)).toBeInTheDocument();
  });
});

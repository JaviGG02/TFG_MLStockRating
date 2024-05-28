import ResizeObserver from "resize-observer-polyfill";
global.ResizeObserver = ResizeObserver;
import React from "react";
import { render, fireEvent, waitFor, screen } from "@testing-library/react";
import PricePredictionChart from "./components/PricePredictionChart/PricePredictionChart";
import FinancialTable from "./components/FinancialTable/FinancialTable";
import BuscadorTicker from "./components/BuscadorTicker/BuscadorTicker";
import OverviewComponent from "./components/OverviewComponent/OverviewComponent";
import RatingDetails from "./components/RatingDetails/RatingDetails";
import App from "./App";
import "@testing-library/jest-dom";
import fetchMock from "jest-fetch-mock";

// TESTS: TU-FE-01. Requisito cubierto: RF-06: Visualización de estadísticas y gráficos
describe("PricePredictionChart", () => {
  const mockDatosFinancieros = {
    TIME_SERIES_MONTHLY_ADJUSTED: {
      "2021-01-01": 100,
      "2021-02-01": 105,
    },
  };

  const mockPredicciones = {
    "2021-03-01": 110,
    "2021-04-01": 115,
  };

  test("renderiza el gráfico cuando se proporcionan datos", () => {
    render(
      <PricePredictionChart
        datosFinancieros={mockDatosFinancieros}
        predicciones={mockPredicciones}
      />,
    );
    // Se displayean las leyendas, por tanto el grafico tambien
    expect(screen.getByText(/RealPrice/i)).toBeInTheDocument();
    expect(screen.getByText(/Prediction/i)).toBeInTheDocument();
  });
});

describe("FinancialTable", () => {
  test("renders financial data correctly", () => {
    const mockData = {
      incomeStatement: [{ fiscalDateEnding: "2021", totalRevenue: "5000000" }],
      balanceSheet: [{ fiscalDateEnding: "2021", totalAssets: "10000000" }],
      cashFlows: [{ fiscalDateEnding: "2021", operatingCashflow: "2000000" }],
    };
    render(<FinancialTable {...mockData} />);
    expect(screen.getByText(/Total Revenue/i)).toBeInTheDocument();
    expect(screen.getByText(/5/i)).toBeInTheDocument();
    expect(screen.getByText(/Total Assets/i)).toBeInTheDocument();
    expect(screen.getByText(/10/i)).toBeInTheDocument();
    expect(screen.getByText(/Operating Cash Flow/i)).toBeInTheDocument();
  });
});

// TESTS: TU-FE-02. Requisito cubierto: RF-07: Búsqueda de empresas
describe("BuscadorTicker", () => {
  test("permite la entrada de un ticker válido", () => {
    const onSearchMock = jest.fn();
    render(<BuscadorTicker onSearch={onSearchMock} />);

    // Simula la entrada de un ticker válido y la presentación del formulario
    fireEvent.change(screen.getByRole("textbox"), {
      target: { value: "AAPL" },
    });
    fireEvent.submit(screen.getByRole("button"));

    // Verifica que la función onSearch se llamó con el ticker en mayúsculas
    expect(onSearchMock).toHaveBeenCalledWith("AAPL");
    expect(screen.queryByText(/Invalid ticker format/)).toBeNull();

    // Verifica div de la animacion
    expect(screen.getByText(/AAPL/)).toBeInTheDocument();
  });

  test("no permite la entrada de un ticker inválido y muestra un mensaje de error", () => {
    const onSearchMock = jest.fn();
    render(<BuscadorTicker onSearch={onSearchMock} />);

    // Simula la entrada de un ticker inválido y la presentación del formulario
    fireEvent.change(screen.getByRole("textbox"), {
      target: { value: "!!@@" },
    });
    fireEvent.submit(screen.getByRole("button"));

    // Verifica que la función onSearch no se llamó
    expect(onSearchMock).not.toHaveBeenCalled();

    // Verifica que se muestre un mensaje de error
    expect(screen.getByText(/Invalid ticker format/)).toBeInTheDocument();
  });
});

// TESTS: TU-FE-03. Requisito cubierto: RF-08: Informacion general sobre la empresa
describe("OverviewComponent", () => {
  const mockOverview = {
    Name: "Apple Inc",
    Symbol: "AAPL",
    Description:
      "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
    Sector: "TECHNOLOGY",
    QuarterlyEarningsGrowthYOY: "10%",
    EPS: "3.89",
    DividendDate: "2021-05-01",
    DividendPerShare: "0.82",
    BookValue: "25.83",
    ReturnOnAssetsTTM: "17%",
    ReturnOnEquityTTM: "22%",
    Currency: "USD",
  };

  const mockCalification = {
    finalRate: 85,
    details: "Highly rated for innovation and market reach",
  };

  test("renders all company overview data correctly", () => {
    render(
      <OverviewComponent
        overview={mockOverview}
        calificacion={mockCalification}
      />,
    );

    expect(screen.getByText(/Apple Inc \(AAPL\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Description/i)).toBeInTheDocument();
    expect(screen.getByText(/EPS/i)).toBeInTheDocument();
    expect(screen.getByText(/3.89/i)).toBeInTheDocument();
    expect(screen.getByText(/Sector/i)).toBeInTheDocument();
    expect(screen.getByText(/TECHNOLOGY/i)).toBeInTheDocument();
    expect(screen.getByText(/Calification/i)).toBeInTheDocument();
    expect(screen.getByText(/85/i)).toBeInTheDocument();
  });
});

// TESTS: TU-FE-04. Requisito cubierto: RF-09: Acceso a información detallada de la calificacion
describe("RatingDetails", () => {
  const mockRatingDetails = {
    finalRate: 30,
    financialHealth: {
      currentRatio: 100,
      debtEquityRatio: 26,
    },
    growth: {
      dividendPayout: 6,
      ebitda: -2,
      freeCashFlow: -90,
      totalRevenue: 0,
    },
    pricePredictionReturn: 0,
    profitability: {
      ROA: 100,
      ROE: 100,
      bookValue: 2,
      netIncome: -7,
    },
  };

  it("should show detailed information when the details button is clicked", () => {
    render(<RatingDetails ratingDetails={mockRatingDetails} />);
    const detailsButton = screen.getByText(/Details/i);
    fireEvent.click(detailsButton);

    expect(screen.getByText(/Calification Summary/i)).toBeInTheDocument();
    expect(screen.getByText(/currentRatio: 100/i)).toBeInTheDocument();
    const netIncomeDiv = screen.getByText(/netIncome: -7/i);
    fireEvent.mouseOver(netIncomeDiv);
    expect(
      screen.getByText(/Indicates how much net profits/i),
    ).toBeInTheDocument();

    const closeButton = screen.getByText(/x/i);
    fireEvent.click(closeButton);
    expect(screen.queryByText(/Calification Summary/i)).toBeNull();
  });
});

// TESTS: TU-FE-05. Requisito cubierto:
fetchMock.enableMocks();

beforeEach(() => {
  fetch.resetMocks();
});

describe("Full App rendering/navigation", () => {
  test("loads and displays the searcher initially", () => {
    render(<App />);
    expect(screen.getByText(/Enter a ticker:/i)).toBeInTheDocument();
  });

  test("loads financial data after entering a valid ticker", async () => {
    const mockData = {
      datos_financieros: {
        OVERVIEW: { Name: "Apple Inc.", Symbol: "AAPL" },
        TIME_SERIES_MONTHLY_ADJUSTED: { "2021-01-01": 100, "2021-02-01": 105 },
        INCOME_STATEMENT: {
          annualReports: [{ fiscalDateEnding: "2021", totalRevenue: "1000" }],
        },
        BALANCE_SHEET: {
          annualReports: [{ fiscalDateEnding: "2021", totalAssets: "5000" }],
        },
        CASH_FLOW: {
          annualReports: [
            { fiscalDateEnding: "2021", operatingCashflow: "750" },
          ],
        },
      },
      predicciones: { "2021-03-01": 110, "2021-04-01": 115 },
      calificacion: { finalRate: 85 },
    };

    fetch.mockResponseOnce(JSON.stringify(mockData));

    render(<App />);
    fireEvent.change(screen.getByRole("textbox"), {
      target: { value: "AAPL" },
    });
    fireEvent.click(screen.getByText(/SEARCH/i));

    await waitFor(() => {
      expect(screen.getByText(/Apple Inc. \(AAPL\)/i)).toBeInTheDocument();
      expect(screen.getByText(/Description/i)).toBeInTheDocument();
      expect(screen.getByText(/Calification/i)).toBeInTheDocument();
      expect(
        screen.getByText(/Annual Financial Statements/i),
      ).toBeInTheDocument();
      expect(screen.getByText(/Income Statement/i)).toBeInTheDocument();
      expect(screen.getByText(/Balance Sheet/i)).toBeInTheDocument();
      expect(screen.getByText(/Cash Flows/i)).toBeInTheDocument();
      expect(screen.getByText(/Total Revenue/i)).toBeInTheDocument();
      expect(screen.getByText(/Operating Cash Flow/i)).toBeInTheDocument();
    });
  });

  test("handles server error correctly", async () => {
    const mockError = {
      Error: "Ticker (INVALID) data not available",
    };

    fetch.mockResponseOnce(JSON.stringify(mockError));

    render(<App />);
    fireEvent.change(screen.getByRole("textbox"), {
      target: { value: "INVALID" },
    });
    fireEvent.click(screen.getByText(/SEARCH/i));

    await waitFor(() => {
      expect(screen.getByText(/ERROR:/i)).toBeInTheDocument();
    });
  });
});

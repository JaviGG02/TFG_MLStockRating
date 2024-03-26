// Funcion para mostrar los atributos financieros. Aquellos comentados se mostrarán en caso de descomentarlos
const FinancialTable = ({ incomeStatement, balanceSheet, cashFlows }) => {
    
    const incomeAttributes = [
        { key: "totalRevenue", name: "Total Revenue" },
        { key: "costOfRevenue", name: "Cost of Revenue" },
        { key: "grossProfit", name: "Gross Profit" },
        { key: "operatingExpenses", name: "Operating Expenses" },
        { key: "researchAndDevelopment", name: "Research and Development" },
        { key: "sellingGeneralAndAdministrative", name: "Selling, General & Administrative" },
        { key: "depreciationAndAmortization", name: "Depreciation and Amortization" },
        { key: "operatingIncome", name: "Operating Income" },
        // { key: "interestExpense", name: "Interest Expense" },
        // { key: "otherNonOperatingIncome", name: "Other Non-Operating Income" },
        // { key: "incomeBeforeTax", name: "Income Before Tax" },
        // { key: "incomeTaxExpense", name: "Income Tax Expense" },
        // { key: "netIncomeFromContinuingOperations", name: "Net Income from Continuing Operations" },
        { key: "netIncome", name: "Net Income" },
        // { key: "comprehensiveIncomeNetOfTax", name: "Comprehensive Income Net of Tax" },
        { key: "ebit", name: "EBIT" },
        { key: "ebitda", name: "EBITDA" }
    ];
  
    const balanceAttributes = [
        { key: "totalAssets", name: "Total Assets" },
        { key: "totalCurrentAssets", name: "Total Current Assets" },
        // { key: "cashAndCashEquivalentsAtCarryingValue", name: "Cash And Cash Equivalents" },
        // { key: "shortTermInvestments", name: "Short Term Investments" },
        // { key: "currentNetReceivables", name: "Net Receivables" },
        // { key: "inventory", name: "Inventory" },
        // { key: "otherCurrentAssets", name: "Other Current Assets" },
        { key: "totalNonCurrentAssets", name: "Total Non Current Assets" },
        // { key: "propertyPlantEquipment", name: "Property, Plant & Equipment" },
        // { key: "goodwill", name: "Goodwill" },
        // { key: "intangibleAssets", name: "Intangible Assets" },
        // { key: "longTermInvestments", name: "Long Term Investments" },
        { key: "totalLiabilities", name: "Total Liabilities" },
        { key: "totalCurrentLiabilities", name: "Total Current Liabilities" },
        // { key: "currentAccountsPayable", name: "Accounts Payable" },
        // { key: "shortLongTermDebtTotal", name: "Short & Long Term Debt" },
        // { key: "otherCurrentLiabilities", name: "Other Current Liabilities" },
        { key: "totalNonCurrentLiabilities", name: "Total Non Current Liabilities" },
        // { key: "longTermDebt", name: "Long Term Debt" },
        // { key: "deferredRevenue", name: "Deferred Revenue Non-Current" },
        // { key: "otherNonCurrentLiabilities", name: "Other Non-Current Liabilities" },
        { key: "totalShareholderEquity", name: "Total Shareholder Equity" },
        { key: "commonStock", name: "Common Stock" },
        { key: "retainedEarnings", name: "Retained Earnings" },
      ];
  
    const cashFlowAttributes = [
        { key: "netIncome", name: "Net Income" },
        // { key: "depreciationDepletionAndAmortization", name: "Depreciation & Amortization" },
        // { key: "changeInReceivables", name: "Change in Receivables" },
        // { key: "changeInInventory", name: "Change in Inventory" },
        // { key: "changeInOperatingAssets", name: "Change in Operating Assets" },
        // { key: "changeInOperatingLiabilities", name: "Change in Operating Liabilities" },
        { key: "operatingCashflow", name: "Operating Cash Flow" },
        { key: "capitalExpenditures", name: "Capital Expenditures" },
        { key: "cashflowFromInvestment", name: "Cash Flow from Investment" },
        { key: "dividendPayout", name: "Dividend Payout" },
        // { key: "paymentsForRepurchaseOfCommonStock", name: "Payments for Repurchase of Common Stock" },
        // { key: "paymentsForRepurchaseOfEquity", name: "Payments for Repurchase of Equity" },
        { key: "cashflowFromFinancing", name: "Cash Flow from Financing" },
        // { key: "changeInCashAndCashEquivalents", name: "Change in Cash and Cash Equivalents" }
    ];
  
    // Función para renderizar los datos de cada informe
    const renderReport = (report, attributes) => (
      <>
        <thead className="column_index">
          <tr>
            <th>Elemento</th>
            {report.map(item => (
              <th key={item.fiscalDateEnding}>{item.fiscalDateEnding.split('-')[0]}</th>
            ))}
          </tr>
        </thead>
        <tbody className="table_values">
          {attributes.map(({ key, name }) => (
            <tr key={key}>
              <td>{name}</td>
              {report.map(item => (
                <td key={`${item.fiscalDateEnding}-${key}`}>{item[key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </>
    );
  
    return (
        <div className="results-div">
            <h1 className="financial-title">Informe Financiero Anual</h1>
            <div className="table-wrapper">
                <p className="financial-caption">Income Statement</p>
                <div className="financial-wrapper">
                    <table className="financial-table">
                        {renderReport(incomeStatement, incomeAttributes)}
                    </table>
                </div>
                <p className="financial-caption">Balance Sheet</p>
                <div className="financial-wrapper">
                    <table className="financial-table">
                        {renderReport(balanceSheet, balanceAttributes)}
                    </table>
                </div>
                <p className="financial-caption">Cash Flows</p>
                <div className="financial-wrapper">
                    <table className="financial-table">
                        {renderReport(cashFlows, cashFlowAttributes)}
                    </table>
                </div>
            </div>
        </div>
    );
  };
  
  export default FinancialTable;
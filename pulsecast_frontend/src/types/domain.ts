export type ForecastRun = {
  runId: string;
  runType?: string;
  horizonStartMonth?: string;
  horizonEndMonth?: string;
  skusCovered?: number;
  mape?: number;
  wape?: number;
  bias?: number;
  mae?: number;
  mapeVsBaselineDelta?: number;
  wapeVsBaselineDelta?: number;
  computedAt?: string;
};

export type ForecastRunValueImpact = {
  runId: string;
  revUpliftEstimate?: number;
  scrapAvoidanceEstimate?: number;
  wcSavingsEstimate?: number;
  productivitySavingsEstimate?: number;
  assumptionsJson?: string | null;
  computedAt?: string;
};

export type ForecastSeriesPoint = {
  yearMonth: string;
  p10?: number | null;
  p50?: number | null;
  p90?: number | null;
  actualUnits?: number | null;
};

export type ForecastSeries = {
  id: string;
  label: string;
  points: ForecastSeriesPoint[];
};

export type InventoryPolicyType = "BASE_STOCK" | "SS_POLICY" | "MIN_MAX" | "CUSTOM" | "RECOMMENDED";

export type InventoryPolicy = {
  policyId?: string;
  skuId: string;
  runId: string;
  scenarioId?: string;
  familyName?: string;
  familyCode?: string;
  skuName?: string;
  skuCode?: string;
  locationId?: string | null;
  policyType: InventoryPolicyType;
  baseStockLevel?: number;
  s?: number;
  S?: number;
  safetyStock?: number;
  expiryDays?: number;
  substitutionAllowed?: boolean;
  substitutionGroupName?: string | null;
  effectiveFrom: string;
  effectiveTo?: string;
  stockoutRiskPercent?: number;
  scrapRiskPercent?: number;
  demandCoverageMonths?: number;
  serviceLevelTarget?: number;
  cycleStockUnits?: number;
  targetStockUnits?: number;
};

export type InventoryPolicyComparison = {
  current: InventoryPolicy;
  previous?: InventoryPolicy;
  deltaSafetyStock?: number;
  deltaScrapRiskPercent?: number;
};

// Alerts
export type AlertSeverity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type AlertStatus = "OPEN" | "ACKNOWLEDGED" | "RESOLVED";
export type AlertType =
  | "LEADING_INDICATOR_SPIKE"
  | "DEMAND_SHOCK"
  | "SUPPLY_RISK"
  | "DATA_STALENESS"
  | "UNKNOWN";

export type Alert = {
  id: string;
  type: AlertType;
  severity: AlertSeverity; // how urgent this alert is for the planner
  status: AlertStatus; // where it sits in the review flow
  title: string;
  summary?: string;
  detailedMessage?: string;
  category?: string;
  createdAt: string;
  updatedAt?: string;
  triggeredAt: string;
  acknowledgedAt?: string;
  relatedRunName?: string;
  relatedScenarioName?: string;
  indicatorName?: string;
  familyName?: string;
  skuName?: string;
};

export type ScenarioStatus =
  | "DRAFT"
  | "SUBMITTED"
  | "APPROVED"
  | "REJECTED"
  | "ACTIVE"
  | "ARCHIVED";

export type ScenarioSummary = {
  scenarioId: string;
  name: string;
  status: ScenarioStatus;
  baseRunId?: string | null;
  upliftPercent?: number | null;
  createdBy: string;
  createdAt: string;
  updatedAt?: string;
};

export type ScenarioDetail = ScenarioSummary & {
  description?: string | null;
  results: ScenarioResultItem[];
  assumptions?: {
    upliftPercent?: number | null;
    notes?: string;
    scope?: {
      type: "ALL" | "FAMILY" | "SKU";
      familyId?: string;
      skuIds?: string[];
    };
    horizon?: {
      fromMonth?: string;
      toMonth?: string;
    };
  };
};

export type ScenarioResultItem = {
  skuId: string;
  yearMonth: string;
  baseRunId?: string | null;
  p10: number;
  p50: number;
  p90: number;
  createdAt: string;
};

export type ScenarioLedgerEntry = {
  ledgerId: string;
  scenarioId: string;
  versionSeq: number;
  actionType:
    | "CREATE"
    | "EDIT"
    | "SUBMIT"
    | "APPROVE"
    | "REJECT"
    | "ARCHIVE"
    | "COMMENT"
    | "RUN_OPTIMIZER";
  actor: string;
  actorRole?: string | null;
  assumptions?: string | null;
  comments?: string | null;
  createdAt: string;
};

export type AlertType =
  | "LEADING_INDICATOR_SPIKE"
  | "DEMAND_SHOCK"
  | "SUPPLY_RISK"
  | "ANOMALY"
  | "THRESHOLD";

export type Alert = {
  alertId: string;
  alertType: AlertType;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  message: string;
  createdAt: string;
  acknowledged?: boolean;
  familyId?: string;
  skuId?: string;
  indicatorId?: string;
};

export type Indicator = {
  indicatorId: string;
  name: string;
  provider: string;
  category?: string;
  frequency: string;
  description?: string;
  geoScope?: string;
  isByo?: boolean;
  status?: string;
  slaFreshnessHours?: number;
  licenseType?: string;
  costEstimatePerMonth?: number;
  tags?: string;
  trustScore?: number;
};

export type IndicatorFreshnessStatus = {
  indicatorId: string;
  indicatorName: string;
  provider: string;
  lastDataTime: string | null;
  lagHours: number | null;
  slaFreshnessHours: number | null;
  isWithinSla: boolean | null;
};

export type IndicatorQualitySummary = {
  indicatorId: string;
  indicatorName: string;
  provider?: string;
  trustScore?: number;
  correlationScore?: number;
  importanceScore?: number;
  isRecommended?: boolean;
};

// Monitor
export type ForecastAccuracyPoint = {
  date: string;
  runId?: string;
  runLabel?: string;
  mape?: number;
  wmape?: number;
  mase?: number;
  accuracyPercent?: number;
};

export type MonitorSummary = {
  overallDataHealth: "GOOD" | "WARNING" | "CRITICAL";
  percentIndicatorsOnTime: number;
  latestForecastAccuracyPercent?: number;
};

// Value / ROI
export type ValueCaseLabel = "CONSERVATIVE" | "BASE" | "STRETCH";

export type ValueRunSummary = {
  runId: string;
  runType?: string;
  periodStart?: string;
  periodEnd?: string;
  familyId?: string | null;
  familyName?: string | null;
  skusCovered?: number;
  revenueUpliftEstimate?: number;
  scrapAvoidanceEstimate?: number;
  workingCapitalSavingsEstimate?: number;
  plannerProductivityHoursSaved?: number;
  totalValueEstimate?: number;
  caseLabel?: ValueCaseLabel;
  computedAt?: string | null;
};

export type ValueScenarioSummary = {
  scenarioId: string;
  scenarioName?: string;
  status?: string;
  linkedRunId?: string | null;
  linkedRunLabel?: string | null;
  revenueUpliftEstimate?: number;
  scrapAvoidanceEstimate?: number;
  workingCapitalSavingsEstimate?: number;
  totalValueEstimate?: number;
  netBenefit?: number;
  currency?: string;
  caseLabel?: ValueCaseLabel;
};

export type ValueBenchmarks = {
  accuracyUpliftPct?: number;
  totalRevenueUplift?: number;
  totalScrapAvoided?: number;
  totalWorkingCapitalImpact?: number;
  plannerTimeSavedHours?: number;
};

// GenAI helper
export type GenaiScope = "FORECAST_RUN" | "SCENARIO" | "VALUE_OVERVIEW" | "FREEFORM";

export type GenaiQuestionContext = {
  scope: GenaiScope; // what part of the app the user is asking about
  runId?: string;
  scenarioId?: string;
  runLabel?: string;
  scenarioName?: string;
};

export type GenaiAskRequest = {
  question: string;
  context: GenaiQuestionContext;
};

export type GenaiAnswerChunk = {
  text: string;
  title?: string;
};

export type GenaiAnswer = {
  answer: string;
  highlights?: GenaiAnswerChunk[];
  caveats?: string;
  sources?: string[];
};

// Roles for view-as navigation
export type UserRole = "PLANNER" | "APPROVER" | "DATA_SCIENTIST";

// Auth
export type AuthUser = {
  id: string;
  email: string;
  fullName?: string;
  role?: string;
  tenantId?: string;
};

export type TokenResponse = {
  accessToken: string;
  tokenType: "bearer";
  user: AuthUser;
};

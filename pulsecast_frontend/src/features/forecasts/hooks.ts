import { useCallback, useEffect, useState } from "react";
import {
  getForecastRunMetadata,
  getForecastSeriesForRun,
  listForecastRuns,
} from "@/api/forecastsApi";
import type {
  ForecastRun,
  ForecastRunValueImpact,
  ForecastSeries,
} from "@/types/domain";
import type { ApiError } from "@/api/httpClient";

type AsyncState<T> = {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
};

export function useForecastRuns() {
  const [state, setState] = useState<AsyncState<ForecastRun[]>>({
    data: null,
    loading: true,
    error: null,
  });

  const load = useCallback(() => {
    setState((s) => ({ ...s, loading: true, error: null }));
    listForecastRuns()
      .then((runs) => setState({ data: runs, loading: false, error: null }))
      .catch((err: ApiError) =>
        setState({ data: null, loading: false, error: err })
      );
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return { ...state, reload: load };
}

type ForecastDetailState = {
  run: ForecastRun | null;
  valueImpact?: ForecastRunValueImpact;
  series: ForecastSeries[];
  loading: boolean;
  error: ApiError | null;
};

type SeriesOptions = {
  skuId?: string;
};

export function useForecastRunDetail(runId: string) {
  const [state, setState] = useState<ForecastDetailState>({
    run: null,
    series: [],
    loading: true,
    error: null,
  });

  const load = useCallback(
    (opts: SeriesOptions = {}) => {
      setState((s) => ({ ...s, loading: true, error: null }));
      Promise.all([
        getForecastRunMetadata(runId),
        getForecastSeriesForRun(runId, { skuId: opts.skuId }),
      ])
        .then(([meta, series]) => {
          setState({
            run: meta.run,
            valueImpact: meta.valueImpact,
            series,
            loading: false,
            error: null,
          });
        })
        .catch((err: ApiError) =>
          setState((s) => ({ ...s, loading: false, error: err }))
        );
    },
    [runId]
  );

  useEffect(() => {
    load();
  }, [load]);

  const changeView = (opts: SeriesOptions) => {
    load(opts);
  };

  return { ...state, changeView };
}

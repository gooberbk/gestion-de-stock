declare module 'react-native-chart-kit' {
  import { ViewStyle } from 'react-native';

  export interface ChartData {
    labels: string[];
    datasets: {
      data: number[];
      color?: (opacity: number) => string;
      strokeWidth?: number;
    }[];
  }

  export interface ChartConfig {
    backgroundColor?: string;
    backgroundGradientFrom?: string;
    backgroundGradientTo?: string;
    decimalPlaces?: number;
    color?: (opacity: number) => string;
    labelColor?: (opacity: number) => string;
    style?: Partial<ViewStyle>;
    propsForDots?: object;
    propsForLabels?: object;
    barPercentage?: number;
    barRadius?: number;
  }

  export interface BarChartProps {
    data: ChartData;
    width: number;
    height: number;
    yAxisLabel?: string;
    yAxisSuffix?: string;
    chartConfig: ChartConfig;
    style?: Partial<ViewStyle>;
    verticalLabelRotation?: number;
    horizontal?: boolean;
    withInnerLines?: boolean;
    withOuterLines?: boolean;
    withVerticalLabels?: boolean;
    withHorizontalLabels?: boolean;
    showBarTops?: boolean;
    fromZero?: boolean;
    segments?: number;
  }

  export const BarChart: React.FC<BarChartProps>;
}

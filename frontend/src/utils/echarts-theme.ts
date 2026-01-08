// ECharts 深色主题配置
export const darkTheme = {
    color: [
        '#2563eb',
        '#38bdf8',
        '#22d3ee',
        '#10b981',
        '#f59e0b',
        '#ef4444',
        '#8b5cf6',
        '#ec4899'
    ],
    backgroundColor: 'transparent',
    textStyle: {
        color: '#e5e7eb',
        fontFamily: 'Manrope, system-ui, sans-serif'
    },
    title: {
        textStyle: {
            color: '#e5e7eb',
            fontWeight: 700
        },
        subtextStyle: {
            color: '#94a3b8'
        }
    },
    line: {
        itemStyle: {
            borderWidth: 2
        },
        lineStyle: {
            width: 3
        },
        symbolSize: 8,
        symbol: 'circle',
        smooth: true
    },
    radar: {
        itemStyle: {
            borderWidth: 2
        },
        lineStyle: {
            width: 3
        },
        symbolSize: 8,
        symbol: 'circle',
        smooth: true,
        axisLine: {
            lineStyle: {
                color: 'rgba(255, 255, 255, 0.08)'
            }
        },
        splitLine: {
            lineStyle: {
                color: 'rgba(255, 255, 255, 0.08)'
            }
        },
        splitArea: {
            areaStyle: {
                color: ['rgba(255, 255, 255, 0.02)', 'rgba(255, 255, 255, 0.04)']
            }
        },
        name: {
            textStyle: {
                color: '#94a3b8'
            }
        }
    },
    bar: {
        itemStyle: {
            barBorderWidth: 0,
            barBorderRadius: [8, 8, 0, 0]
        }
    },
    pie: {
        itemStyle: {
            borderWidth: 0,
            borderRadius: 8
        },
        label: {
            color: '#e5e7eb'
        }
    },
    scatter: {
        itemStyle: {
            borderWidth: 0,
            borderRadius: 8
        }
    },
    boxplot: {
        itemStyle: {
            borderWidth: 0,
            borderRadius: 8
        }
    },
    parallel: {
        itemStyle: {
            borderWidth: 0,
            borderRadius: 8
        }
    },
    sankey: {
        itemStyle: {
            borderWidth: 0,
            borderRadius: 8
        }
    },
    funnel: {
        itemStyle: {
            borderWidth: 0,
            borderRadius: 8
        }
    },
    gauge: {
        itemStyle: {
            borderWidth: 0,
            borderRadius: 8
        }
    },
    candlestick: {
        itemStyle: {
            color: '#10b981',
            color0: '#ef4444',
            borderColor: '#10b981',
            borderColor0: '#ef4444',
            borderWidth: 2
        }
    },
    graph: {
        itemStyle: {
            borderWidth: 0,
            borderRadius: 8
        },
        lineStyle: {
            width: 2,
            color: 'rgba(255, 255, 255, 0.2)'
        },
        symbolSize: 8,
        symbol: 'circle',
        smooth: true,
        color: [
            '#2563eb',
            '#38bdf8',
            '#22d3ee',
            '#10b981',
            '#f59e0b',
            '#ef4444',
            '#8b5cf6',
            '#ec4899'
        ],
        label: {
            color: '#e5e7eb'
        }
    },
    map: {
        itemStyle: {
            areaColor: 'rgba(255, 255, 255, 0.04)',
            borderColor: 'rgba(255, 255, 255, 0.16)',
            borderWidth: 1
        },
        label: {
            color: '#e5e7eb'
        },
        emphasis: {
            itemStyle: {
                areaColor: 'rgba(37, 99, 235, 0.3)',
                borderColor: '#2563eb',
                borderWidth: 2
            },
            label: {
                color: '#ffffff'
            }
        }
    },
    geo: {
        itemStyle: {
            areaColor: 'rgba(255, 255, 255, 0.04)',
            borderColor: 'rgba(255, 255, 255, 0.16)',
            borderWidth: 1
        },
        label: {
            color: '#e5e7eb'
        },
        emphasis: {
            itemStyle: {
                areaColor: 'rgba(37, 99, 235, 0.3)',
                borderColor: '#2563eb',
                borderWidth: 2
            },
            label: {
                color: '#ffffff'
            }
        }
    },
    categoryAxis: {
        axisLine: {
            show: true,
            lineStyle: {
                color: 'rgba(255, 255, 255, 0.08)'
            }
        },
        axisTick: {
            show: false
        },
        axisLabel: {
            show: true,
            color: '#94a3b8'
        },
        splitLine: {
            show: false
        },
        splitArea: {
            show: false
        }
    },
    valueAxis: {
        axisLine: {
            show: false
        },
        axisTick: {
            show: false
        },
        axisLabel: {
            show: true,
            color: '#94a3b8'
        },
        splitLine: {
            show: true,
            lineStyle: {
                color: 'rgba(255, 255, 255, 0.08)',
                type: 'dashed'
            }
        },
        splitArea: {
            show: false
        }
    },
    logAxis: {
        axisLine: {
            show: false
        },
        axisTick: {
            show: false
        },
        axisLabel: {
            show: true,
            color: '#94a3b8'
        },
        splitLine: {
            show: true,
            lineStyle: {
                color: 'rgba(255, 255, 255, 0.08)'
            }
        },
        splitArea: {
            show: false
        }
    },
    timeAxis: {
        axisLine: {
            show: true,
            lineStyle: {
                color: 'rgba(255, 255, 255, 0.08)'
            }
        },
        axisTick: {
            show: false
        },
        axisLabel: {
            show: true,
            color: '#94a3b8'
        },
        splitLine: {
            show: false
        },
        splitArea: {
            show: false
        }
    },
    toolbox: {
        iconStyle: {
            borderColor: '#94a3b8'
        },
        emphasis: {
            iconStyle: {
                borderColor: '#e5e7eb'
            }
        }
    },
    legend: {
        right: 20,
        top: 20,
        orient: 'vertical',
        textStyle: {
            color: '#94a3b8'
        },
        pageTextStyle: {
            color: '#94a3b8'
        }
    },
    tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        borderColor: 'rgba(255, 255, 255, 0.16)',
        borderWidth: 1,
        textStyle: {
            color: '#e5e7eb'
        },
        axisPointer: {
            lineStyle: {
                color: 'rgba(255, 255, 255, 0.2)',
                width: 2
            },
            crossStyle: {
                color: 'rgba(255, 255, 255, 0.2)',
                width: 2
            }
        }
    },
    timeline: {
        show: false,
        lineStyle: {
            color: 'transparent'
        },
        itemStyle: {
            color: 'transparent'
        },
        controlStyle: {
            show: false
        },
        label: {
            show: false
        }
    },
    visualMap: {
        textStyle: {
            color: '#e5e7eb'
        }
    },
    markPoint: {
        label: {
            color: '#e5e7eb'
        },
        emphasis: {
            label: {
                color: '#e5e7eb'
            }
        }
    }
}

// ECharts 亮色主题配置
export const lightTheme = {
    color: [
        '#2563eb',
        '#0ea5e9',
        '#0891b2',
        '#059669',
        '#d97706',
        '#dc2626',
        '#7c3aed',
        '#db2777'
    ],
    backgroundColor: 'transparent',
    textStyle: {
        color: '#0f172a',
        fontFamily: 'Manrope, system-ui, sans-serif'
    },
    title: {
        textStyle: {
            color: '#0f172a',
            fontWeight: 700
        },
        subtextStyle: {
            color: '#64748b'
        }
    },
    line: {
        itemStyle: {
            borderWidth: 2
        },
        lineStyle: {
            width: 3
        },
        symbolSize: 8,
        symbol: 'circle',
        smooth: true
    },
    radar: {
        itemStyle: {
            borderWidth: 2
        },
        lineStyle: {
            width: 3
        },
        symbolSize: 8,
        symbol: 'circle',
        smooth: true,
        axisLine: {
            lineStyle: {
                color: 'rgba(15, 23, 42, 0.12)'
            }
        },
        splitLine: {
            lineStyle: {
                color: 'rgba(15, 23, 42, 0.12)'
            }
        },
        splitArea: {
            areaStyle: {
                color: ['rgba(15, 23, 42, 0.02)', 'rgba(15, 23, 42, 0.04)']
            }
        },
        name: {
            textStyle: {
                color: '#64748b'
            }
        }
    },
    bar: {
        itemStyle: {
            barBorderWidth: 0,
            barBorderRadius: [8, 8, 0, 0]
        }
    },
    pie: {
        itemStyle: {
            borderWidth: 0,
            borderRadius: 8
        },
        label: {
            color: '#0f172a'
        }
    },
    scatter: {
        itemStyle: {
            borderWidth: 0,
            borderRadius: 8
        }
    },
    categoryAxis: {
        axisLine: {
            show: true,
            lineStyle: {
                color: 'rgba(15, 23, 42, 0.12)'
            }
        },
        axisTick: {
            show: false
        },
        axisLabel: {
            show: true,
            color: '#64748b'
        },
        splitLine: {
            show: false
        },
        splitArea: {
            show: false
        }
    },
    valueAxis: {
        axisLine: {
            show: false
        },
        axisTick: {
            show: false
        },
        axisLabel: {
            show: true,
            color: '#64748b'
        },
        splitLine: {
            show: true,
            lineStyle: {
                color: 'rgba(15, 23, 42, 0.08)',
                type: 'dashed'
            }
        },
        splitArea: {
            show: false
        }
    },
    logAxis: {
        axisLine: {
            show: false
        },
        axisTick: {
            show: false
        },
        axisLabel: {
            show: true,
            color: '#64748b'
        },
        splitLine: {
            show: true,
            lineStyle: {
                color: 'rgba(15, 23, 42, 0.08)'
            }
        },
        splitArea: {
            show: false
        }
    },
    timeAxis: {
        axisLine: {
            show: true,
            lineStyle: {
                color: 'rgba(15, 23, 42, 0.12)'
            }
        },
        axisTick: {
            show: false
        },
        axisLabel: {
            show: true,
            color: '#64748b'
        },
        splitLine: {
            show: false
        },
        splitArea: {
            show: false
        }
    },
    toolbox: {
        iconStyle: {
            borderColor: '#64748b'
        },
        emphasis: {
            iconStyle: {
                borderColor: '#0f172a'
            }
        }
    },
    legend: {
        right: 20,
        top: 20,
        orient: 'vertical',
        textStyle: {
            color: '#64748b'
        },
        pageTextStyle: {
            color: '#64748b'
        }
    },
    tooltip: {
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: 'rgba(15, 23, 42, 0.16)',
        borderWidth: 1,
        textStyle: {
            color: '#0f172a'
        },
        axisPointer: {
            lineStyle: {
                color: 'rgba(15, 23, 42, 0.2)',
                width: 2
            },
            crossStyle: {
                color: 'rgba(15, 23, 42, 0.2)',
                width: 2
            }
        }
    },
    timeline: {
        show: false,
        lineStyle: {
            color: 'transparent'
        },
        itemStyle: {
            color: 'transparent'
        },
        controlStyle: {
            show: false
        },
        label: {
            show: false
        }
    },
    visualMap: {
        textStyle: {
            color: '#0f172a'
        }
    },
    markPoint: {
        label: {
            color: '#0f172a'
        },
        emphasis: {
            label: {
                color: '#0f172a'
            }
        }
    }
}

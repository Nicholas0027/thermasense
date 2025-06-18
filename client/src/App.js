// file: client/src/App.js
import React, { useState, useEffect, useRef, useCallback } from 'react';
import Chart from 'chart.js/auto';
import 'chartjs-adapter-date-fns';

function App() {
    // --- 状态管理 (State Management) ---
    const [userId, setUserId] = useState(null);
    const [view, setView] = useState('voting'); // 'voting' 或 'dashboard'
    const [zones, setZones] = useState([]);
    const [currentZoneId, setCurrentZoneId] = useState('');
    const [zoneData, setZoneData] = useState(null);
    const [stats, setStats] = useState({ "-1": 0, "0": 0, "1": 0 });
    const [message, setMessage] = useState('');
    
    const chartRef = useRef(null);
    const chartInstance = useRef(null);

    // --- 数据获取与初始化 (Data Fetching & Initialization) ---
    // 首次加载时: 获取用户ID和分区列表
    useEffect(() => {
        let currentUserId = localStorage.getItem('thermasense_userId');
        if (!currentUserId) {
            currentUserId = crypto.randomUUID();
            localStorage.setItem('thermasense_userId', currentUserId);
        }
        setUserId(currentUserId);

        const fetchZones = async () => {
            try {
                const response = await fetch('/api/zones/');
                if (!response.ok) throw new Error('无法获取分区列表');
                const data = await response.json();
                setZones(data);
                if (data.length > 0) {
                    setCurrentZoneId(data[0].zone_id);
                }
            } catch (error) {
                setMessage(`错误: ${error.message}`);
            }
        };
        fetchZones();
    }, []);

    // 获取并刷新数据的核心函数 (使用useCallback进行性能优化)
    const fetchZoneData = useCallback(async () => {
        if (!currentZoneId) return;
        try {
            const [statusRes, statsRes] = await Promise.all([
                fetch(`/api/zones/${currentZoneId}/status`),
                fetch(`/api/zones/${currentZoneId}/stats`)
            ]);

            if (!statusRes.ok || !statsRes.ok) throw new Error('无法获取分区数据');

            const statusData = await statusRes.json();
            const statsData = await statsRes.json();

            setZoneData(statusData);
            setStats(statsData);

        } catch (error) {
             setMessage(`数据刷新失败: ${error.message}`);
        }
    }, [currentZoneId]);

    // 依赖于currentZoneId变化，立即获取一次数据
    useEffect(() => {
        fetchZoneData();
    }, [fetchZoneData]);

    // 在仪表盘视图下，设置一个定时器，每5秒刷新一次数据
    useEffect(() => {
        let intervalId = null;
        if (view === 'dashboard') {
            const id = setInterval(fetchZoneData, 5000); // 每5秒刷新
            intervalId = id;
        }
        // 组件卸载或视图切换时，清除定时器，避免内存泄漏
        return () => clearInterval(intervalId); 
    }, [view, fetchZoneData]);

    // 更新图表的逻辑
    useEffect(() => {
        if (view === 'dashboard' && chartRef.current) {
            const chartData = {
                labels: ['偏冷', '舒适', '偏热'],
                datasets: [{
                    data: [stats["-1"], stats["0"], stats["1"]],
                    backgroundColor: ['#60a5fa', '#34d399', '#f87171'],
                    borderColor: '#fff',
                    borderWidth: 2,
                }]
            };

            if (chartInstance.current) {
                chartInstance.current.data = chartData;
                chartInstance.current.update();
            } else {
                chartInstance.current = new Chart(chartRef.current, {
                    type: 'doughnut', data: chartData,
                    options: {
                        responsive: true, maintainAspectRatio: false,
                        plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, padding: 15 } } },
                        cutout: '60%',
                    }
                });
            }
        }
    }, [stats, view]); // 依赖项加入view，确保图表只在dashboard时渲染

    // --- 事件处理 (Event Handlers) ---
    const handleVote = async (voteValue) => {
        if (!userId || !currentZoneId) return;
        setMessage('');
        try {
            const response = await fetch('/api/vote/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, zone_id: currentZoneId, vote_value: voteValue }),
            });
            if (!response.ok) {
                // 【优化】更详细的错误日志
                const errorData = await response.json().catch(() => ({detail: "无法解析服务器错误信息"}));
                console.error("API Error:", errorData);
                throw new Error(errorData.detail || `服务器错误: ${response.status}`);
            }
            setView('dashboard'); // 投票成功后切换视图
        } catch (error) {
            setMessage(`投票失败: ${error.message}`);
        }
    };

    const handleZoneChange = (event) => {
        setCurrentZoneId(event.target.value);
        setView('voting'); // 切换区域后返回投票界面
        setMessage('');
    };
    
    // --- 界面渲染 (UI Rendering) ---
    return (
        <div className="bg-neutral-50 text-neutral-800 flex flex-col items-center justify-center min-h-screen p-4 font-sans">
            <div className="w-full max-w-md mx-auto">
                <header className="text-center mb-6">
                    <h1 className="text-3xl font-bold text-neutral-700">ThermaSense</h1>
                    <p className="text-neutral-500 mt-1">智能感知您的冷暖</p>
                </header>
                <main className="bg-white rounded-2xl shadow-lg p-6 w-full min-h-[500px]">
                    {zones.length > 0 ? (
                        <div className="mb-6">
                            <label htmlFor="zone-switcher" className="block text-sm font-medium text-neutral-600 mb-2">请选择您所在的区域</label>
                            <select id="zone-switcher" value={currentZoneId} onChange={handleZoneChange} className="w-full bg-neutral-100 border-neutral-200 border rounded-lg p-2 focus:ring-2 focus:ring-blue-400 focus:outline-none">
                                {zones.map(zone => <option key={zone.zone_id} value={zone.zone_id}>{zone.name}</option>)}
                            </select>
                        </div>
                    ) : <p className="text-center text-gray-500">正在加载区域列表...</p>}
                    
                    <div id="content-area">
                        {view === 'voting' && zoneData ? (
                            <div id="voting-view" className="animate-fade-in">
                                <div className="text-center mb-6">
                                    <p className="text-neutral-600">您当前在 <strong className="text-blue-600">{zoneData.name}</strong></p>
                                    <p className="text-4xl font-bold mt-2 text-neutral-800">
                                        {typeof zoneData.current_temp === 'number' ? zoneData.current_temp.toFixed(1) : '...'}
                                        &deg;C
                                    </p>
                                </div>
                                <div className="text-center mb-4 text-lg font-medium">您感觉如何？</div>
                                <div className="grid grid-cols-3 gap-3">
                                    <button onClick={() => handleVote(-1)} className="vote-btn flex flex-col items-center p-3 bg-blue-100 text-blue-800 rounded-lg shadow-sm hover:scale-105 transition-transform">
                                        <span className="text-3xl">🥶</span><span className="text-xs mt-1">偏冷</span>
                                    </button>
                                    <button onClick={() => handleVote(0)} className="vote-btn flex flex-col items-center p-3 bg-emerald-100 text-emerald-800 rounded-lg shadow-sm hover:scale-105 transition-transform">
                                        <span className="text-3xl">😊</span><span className="text-xs mt-1">舒适</span>
                                    </button>
                                    <button onClick={() => handleVote(1)} className="vote-btn flex flex-col items-center p-3 bg-red-100 text-red-800 rounded-lg shadow-sm hover:scale-105 transition-transform">
                                        <span className="text-3xl">🥵</span><span className="text-xs mt-1">偏热</span>
                                    </button>
                                </div>
                            </div>
                        ) : view === 'dashboard' && zoneData ? (
                            <div id="dashboard-view" className="animate-fade-in">
                                <div className="text-center mb-4">
                                    <p className="text-neutral-600">收到！这是 <strong className="text-blue-600">{zoneData.name}</strong> 的当前状态</p>
                                </div>
                                <div className="flex justify-around items-center text-center my-4">
                                    <div>
                                        <p className="text-sm text-gray-500">当前温度</p>
                                        <p className="text-2xl font-bold">
                                            {typeof zoneData.current_temp === 'number' ? zoneData.current_temp.toFixed(1) : '...'}
                                            &deg;C
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-500">推荐温度</p>
                                        <p className="text-2xl font-bold text-green-600">
                                            {typeof zoneData.recommended_temp === 'number' ? zoneData.recommended_temp.toFixed(1) : '...'}
                                            &deg;C
                                        </p>
                                    </div>
                                </div>
                                <div className="relative mx-auto w-full h-48 max-w-xs mb-4">
                                    <canvas ref={chartRef}></canvas>
                                </div>
                                <button onClick={() => setView('voting')} className="w-full mt-4 bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600">返回投票</button>
                            </div>
                        ) : <div className="text-center text-gray-500">正在加载...</div> }
                        {message && <p className="text-center text-sm text-red-500 mt-4">{message}</p>}
                    </div>
                </main>
            </div>
        </div>
    );
}
export default App;
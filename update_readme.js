//  update_readme.js
const fs = require('fs');
const path = require('path');

const reportPath = path.join(__dirname, 'report.md');
const readmePath = path.join(__dirname, 'README.md');

// ===== 1) 生成「配置源对比」表格（基于实际产物，与 report.md 无关，必定执行）=====
function countSites(p) {
    try {
        const d = JSON.parse(fs.readFileSync(path.join(__dirname, p), 'utf-8'));
        const sites = d.api_site || {};
        let adult = 0;
        for (const v of Object.values(sites)) {
            const n = (v.name || '').toLowerCase();
            if (v.is_adult || v.isAdult || (v.name || '').includes('🔞') ||
                n.startsWith('av') || n.includes('av-')) {
                adult++;
            }
        }
        return { total: Object.keys(sites).length, adult };
    } catch (e) {
        return null;
    }
}

const cfgDefs = [
    { label: '🏆 Top20 (output_top20)', file: 'output_top20.json', scene: '推荐：综合评分最优的 20 个节点（同名仅留最优变体）' },
    { label: '全量 (output)',           file: 'output.json',       scene: '完整功能、最大兼容性（保留多域名变体）' },
    { label: '主配置 (LunaTV-config)',   file: 'LunaTV-config.json', scene: 'App 默认配置：手工精选 + 全量变体' },
];

let cfgRows = '';
for (const c of cfgDefs) {
    const r = countSites(c.file);
    if (!r) {
        cfgRows += `| ${c.label} | - | - | ${c.scene} |\n`;
        continue;
    }
    const adultTxt = r.adult > 0 ? `含 ${r.adult} 条` : '已过滤';
    cfgRows += `| ${c.label} | ${r.total} 个 | ${adultTxt} | ${c.scene} |\n`;
}
const cfgBlock =
    `## 📦 配置源对比\n\n` +
    `（以下内容由 CI 自动生成，请勿手动修改）\n\n` +
    `| 配置源 | 资源数量 | 成人内容 | 适用场景 |\n| - | - | - | - |\n${cfgRows}`;

// ===== 2) 尝试从 report.md 生成「API 状态」表格（失败仅告警，不影响配置对比表）=====
function buildApiBlock() {
    if (!fs.existsSync(reportPath)) {
        console.error('⚠️ report.md 不存在，跳过 API 状态表格更新（请先运行 check_api.js）');
        return null;
    }
    const reportContent = fs.readFileSync(reportPath, 'utf-8');
    // 容错：表格可能在文件末尾或紧跟 <details>，不强制要求空行
    const tableMatch = reportContent.match(/\| 状态 \|[\s\S]+?(?=\n\n|<\/details>|$)/);
    if (!tableMatch) {
        console.error('⚠️ report.md 中未找到表格，跳过 API 状态表格更新');
        return null;
    }
    let tableMd = tableMatch[0].trim();

    const lines = tableMd.split('\n');
    const header = lines.slice(0, 2);
    const rows = lines.slice(2);

    const rowsWithData = rows.map(line => {
        const cols = line.split('|').map(c => c.trim());
        if (cols.length < 10) return null;                 // 跳过非数据行（列数不足）
        const status = cols[1];
        const apiName = cols[2];
        const apiAddress = cols[4];
        const successCount = parseInt(cols[6]) || 0;
        const failCount = parseInt(cols[7]) || 0;
        const availabilityStr = cols[8] || '0%';
        const availabilityMatch = availabilityStr.match(/(\d+\.?\d*)%/);
        const availability = availabilityMatch ? parseFloat(availabilityMatch[1]) : 0;
        return {
            line, cols, status, apiName, apiAddress, successCount, failCount,
            availability, consecutiveFailDays: 0, isSuccess: (status || '').includes('✅')
        };
    }).filter(Boolean);

    rowsWithData.sort((a, b) => {
        if (Math.abs(b.availability - a.availability) > 0.01) return b.availability - a.availability;
        return a.apiName.localeCompare(b.apiName);
    });

    tableMd = [...header, ...rowsWithData.map(r => r.line)].join('\n');

    const totalApis = rowsWithData.length;
    const successApis = rowsWithData.filter(r => r.isSuccess).length;
    const failApis = totalApis - successApis;
    const perfectApis = rowsWithData.filter(r => r.availability === 100).length;
    const highAvailability = rowsWithData.filter(r => r.availability >= 80 && r.availability < 100).length;
    const mediumAvailability = rowsWithData.filter(r => r.availability >= 50 && r.availability < 80).length;
    const lowAvailability = rowsWithData.filter(r => r.availability < 50).length;
    const averageAvailability = totalApis > 0 ? (rowsWithData.reduce((s, r) => s + r.availability, 0) / totalApis).toFixed(1) : 0;

    const now = new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString().replace('T', ' ').slice(0, 16) + ' CST';

    const block =
        `## API 状态（最近更新：${now}）\n\n` +
        `- 总 API 数量：${totalApis}\n` +
        `- 成功 API 数量：${successApis}\n` +
        `- 失败 API 数量：${failApis}\n` +
        `- 平均可用率：${averageAvailability}%\n` +
        `- 完美可用率（100%）：${perfectApis} 个\n` +
        `- 高可用率（80%-99%）：${highAvailability} 个\n` +
        `- 中等可用率（50%-79%）：${mediumAvailability} 个\n` +
        `- 低可用率（<50%）：${lowAvailability} 个\n\n` +
        `<div style="font-size: 11px;">\n\n` +
        `<!-- API_TABLE_START -->\n${tableMd}\n<!-- API_TABLE_END -->`;

    return { block, stats: { totalApis, successApis, failApis, averageAvailability, perfectApis, highAvailability, mediumAvailability, lowAvailability, rowsWithData } };
}

const api = buildApiBlock();

// ===== 3) 读取 README 并替换（配置对比必定更新；API 表仅在可解析时更新）=====
let readmeContent = fs.existsSync(readmePath) ? fs.readFileSync(readmePath, 'utf-8') : "";

if (readmeContent.includes('<!-- CONFIG_COMPARE_START -->') && readmeContent.includes('<!-- CONFIG_COMPARE_END -->')) {
    readmeContent = readmeContent.replace(
        /<!-- CONFIG_COMPARE_START -->[\s\S]*?<!-- CONFIG_COMPARE_END -->/,
        `<!-- CONFIG_COMPARE_START -->\n${cfgBlock}\n<!-- CONFIG_COMPARE_END -->`
    );
    console.log('✅ README.md 已更新「配置源对比」表格（真实统计）');
} else {
    readmeContent += `\n\n<!-- CONFIG_COMPARE_START -->\n${cfgBlock}\n<!-- CONFIG_COMPARE_END -->\n`;
    console.log('⚠️ README.md 未找到配置对比标记，已自动追加');
}

if (api) {
    if (readmeContent.includes('<!-- API_TABLE_START -->') && readmeContent.includes('<!-- API_TABLE_END -->')) {
        readmeContent = readmeContent.replace(
            /## API 状态（最近更新：[^\n]+）[\s\S]*?<!-- API_TABLE_END -->/,
            api.block
        );
        console.log('✅ README.md 已更新 API 状态表格（按可用率排序）');
    } else {
        readmeContent += `\n\n${api.block}\n`;
        console.log('⚠️ README.md 未找到 API 标记，已自动追加');
    }
}

fs.writeFileSync(readmePath, readmeContent, 'utf-8');

// ===== 4) 输出摘要（仅当 API 表成功解析）=====
if (api) {
    const s = api.stats;
    console.log(`\n📊 统计摘要：`);
    console.log(`- 平均可用率：${s.averageAvailability}%`);
    console.log(`- 完美可用率 API：${s.perfectApis} 个`);
    console.log(`- 高可用率 API：${s.highAvailability} 个`);
    console.log(`- 中等可用率 API：${s.mediumAvailability} 个`);
    console.log(`- 低可用率 API：${s.lowAvailability} 个`);
    console.log(`\n🏆 可用率最高的前10个API：`);
    s.rowsWithData.slice(0, 10).forEach((row, i) => console.log(`${i + 1}. ${row.apiName}: ${row.availability}%`));
    console.log(`\n⚠️ 可用率最低的后5个API：`);
    s.rowsWithData.slice(-5).forEach((row, i) => console.log(`${s.rowsWithData.length - 4 + i}. ${row.apiName}: ${row.availability}%`));
}

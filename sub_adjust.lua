--[[
批量处理字幕时间轴脚本

该脚本用于批量将指定目录中的所有ASS、SSA、SRT字幕文件的时间轴根据配置延迟或提前。

使用方法：
1. 将此脚本保存为 .lua 文件。
2. 打开脚本，编辑常量配置部分以适应你的需求。
   - directory: 设置字幕文件所在的目录路径。
   - shift_value: 设置时间偏移量（秒）。正值表示延迟，负值表示提前。
   - shift_direction: 设置时间轴调整方向。可以是 "delay"（延后）或 "advance"（提前）。
   - layer_numbers: 设置要应用的字幕层。可以是 "all"，表示应用到所有层；或者是一个逗号分隔的数字字符串（如 "0,1,2"），表示只应用于特定层（只适用于ASS和SSA格式）。
3. 在Aegisub中加载并运行该脚本，脚本将处理指定目录下的所有 .ass、.ssa 和 .srt 文件，并根据你设定的常量配置调整字幕时间轴。

注意：
- 脚本执行后会覆盖原始字幕文件，因此在运行脚本之前建议备份文件。
- 本脚本主要使用Lua标准库实现，不依赖Aegisub的特定功能，因此可以在任何支持Lua引擎的环境中单独运行。
]]

script_name = "批量处理字幕时间轴 (配合aegisub自动化功能使用)"
script_description = "批量将目录中所有字幕文件的时间轴根据配置延迟或提前，使用前务必参照使用方法编辑脚本内各常量值"
script_author = "Jade (i@kayanoai.net)"
script_version = "2.3"

local lfs = require("lfs")  -- 引入 Lua 文件系统模块

-- 常量配置
local directory = "e:\\sub-adjust\\"  -- 字幕文件所在目录
local shift_value = 10.5 * 1000  -- 时间偏移（毫秒）
local shift_direction = "delay"  -- 方向：延后 ("delay") 或 提前 ("advance")
local layer_numbers = "all"  -- "all" 或者逗号分隔的数字字符串（如 "0,1,2"）

-- 将时间字符串转换为毫秒（用于ASS和SSA格式）
local function time_to_ms(h, m, s, cs)
    return ((tonumber(h) * 3600) + (tonumber(m) * 60) + tonumber(s)) * 1000 + tonumber(cs) * 10
end

-- 将毫秒转换为时间字符串（用于ASS和SSA格式）
local function ms_to_time(ms)
    local h = math.floor(ms / 3600000)
    local m = math.floor((ms % 3600000) / 60000)
    local s = math.floor((ms % 60000) / 1000)
    local cs = math.floor((ms % 1000) / 10)
    return string.format("%01d:%02d:%02d.%02d", h, m, s, cs)
end

-- 将时间字符串转换为毫秒（用于SRT格式）
local function srt_time_to_ms(h, m, s, ms)
    return ((tonumber(h) * 3600) + (tonumber(m) * 60) + tonumber(s)) * 1000 + tonumber(ms)
end

-- 将毫秒转换为时间字符串（用于SRT格式）
local function ms_to_srt_time(ms)
    local h = string.format("%02d", math.floor(ms / 3600000))
    local m = string.format("%02d", math.floor((ms % 3600000) / 60000))
    local s = string.format("%02d", math.floor((ms % 60000) / 1000))
    local ms = string.format("%03d", ms % 1000)
    return string.format("%s:%s:%s,%s", h, m, s, ms)
end

-- 解析 layer_numbers 常量
local function parse_layers(layer_numbers)
    local layers = {}
    if layer_numbers ~= "all" then
        for layer in layer_numbers:gmatch("%d+") do
            table.insert(layers, tonumber(layer))
        end
    end
    return layers
end

-- 检查某个 layer 是否在给定的 layer 列表中
local function is_layer_included(layer, layers)
    if #layers == 0 then
        return true  -- 当 layers 列表为空时，表示 "all" 层
    else
        for _, l in ipairs(layers) do
            if l == layer then
                return true
            end
        end
    end
    return false
end

-- 处理ASS和SSA字幕文件
local function process_ass_ssa_file(filepath, adjusted_shift_value, layers)
    local infile = io.open(filepath, "r")
    if not infile then
        aegisub.log("Error opening file: %s\n", filepath)
        return
    end

    local lines = {}
    for line in infile:lines() do
        -- 查找并调整字幕行的时间轴
        local layer, start_time, end_time = line:match("Dialogue: (%d+),(%d+:%d+:%d+%.%d+),(%d+:%d+:%d+%.%d+),")
        layer = tonumber(layer)
        
        if start_time and end_time and is_layer_included(layer, layers) then
            local h1, m1, s1, cs1 = start_time:match("(%d+):(%d+):(%d+)%.(%d+)")
            local h2, m2, s2, cs2 = end_time:match("(%d+):(%d+):(%d+)%.(%d+)")

            local start_ms = time_to_ms(h1, m1, s1, cs1) + adjusted_shift_value
            local end_ms = time_to_ms(h2, m2, s2, cs2) + adjusted_shift_value

            line = line:gsub(start_time, ms_to_time(start_ms))
            line = line:gsub(end_time, ms_to_time(end_ms))
        end
        table.insert(lines, line)
    end
    infile:close()

    -- 打开文件进行写入
    local outfile = io.open(filepath, "w")
    for _, line in ipairs(lines) do
        outfile:write(line .. "\n")
    end
    outfile:close()
end

-- 处理SRT字幕文件
local function process_srt_file(filepath, adjusted_shift_value)
    local infile = io.open(filepath, "r")
    if not infile then
        aegisub.log("Error opening file: %s\n", filepath)
        return
    end

    local lines = {}
    for line in infile:lines() do
        -- 查找并调整字幕行的时间轴
        local start_time, end_time = line:match("(%d+:%d+:%d+,%d+) --> (%d+:%d+:%d+,%d+)")
        
        if start_time and end_time then
            local h1, m1, s1, ms1 = start_time:match("(%d+):(%d+):(%d+),(%d+)")
            local h2, m2, s2, ms2 = end_time:match("(%d+):(%d+):(%d+),(%d+)")

            local start_ms = srt_time_to_ms(h1, m1, s1, ms1) + adjusted_shift_value
            local end_ms = srt_time_to_ms(h2, m2, s2, ms2) + adjusted_shift_value

            line = line:gsub(start_time, ms_to_srt_time(start_ms))
            line = line:gsub(end_time, ms_to_srt_time(end_ms))
        end
        table.insert(lines, line)
    end
    infile:close()

    -- 打开文件进行写入
    local outfile = io.open(filepath, "w")
    for _, line in ipairs(lines) do
        outfile:write(line .. "\n")
    end
    outfile:close()
end

function shift_times_in_directory()
    -- 根据方向设置偏移量
    local adjusted_shift_value = shift_direction == "advance" and -shift_value or shift_value
    local layers = parse_layers(layer_numbers)

    -- 遍历目录中的所有字幕文件
    for file in lfs.dir(directory) do
        local filepath = directory .. file
        if file:match("%.ass$") or file:match("%.ssa$") then
            aegisub.log("Processing ASS/SSA: %s\n", filepath)
            process_ass_ssa_file(filepath, adjusted_shift_value, layers)
        elseif file:match("%.srt$") then
            aegisub.log("Processing SRT: %s\n", filepath)
            process_srt_file(filepath, adjusted_shift_value)
        end
    end

    aegisub.set_undo_point(script_name)
end

-- 将函数注册到Aegisub
aegisub.register_macro(script_name, script_description, shift_times_in_directory)

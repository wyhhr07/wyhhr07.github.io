// Object.groupBy
if (!Object.groupBy) {
    Object.groupBy = function (items, callback) {
        const result = {};
        for (const item of items) {
            const key = callback(item);
            if (!result[key]) result[key] = [];
            result[key].push(item);
        }
        return result;
    };
}

// Map.groupBy
if (!Map.groupBy) {
    Map.groupBy = function (items, callback) {
        const map = new Map();
        for (const item of items) {
            const key = callback(item);
            if (!map.has(key)) {
                map.set(key, []);
            }
            map.get(key).push(item);
        }
        return map;
    };
}
if (!Object.groupBy) {
    Object.groupBy = function (items, callback) {
        const result = {};

        for (const item of items) {
            const key = callback(item);
            if (!result[key]) {
                result[key] = [];
            }
            result[key].push(item);
        }

        return result;
    };
}
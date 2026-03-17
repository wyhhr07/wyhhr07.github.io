// Object.groupBy
if (!Object.groupBy) {
    Object.groupBy = function(items, fn) {
      const obj = {};
      for (const item of items) {
        const key = fn(item);
        (obj[key] ||= []).push(item);
      }
      return obj;
    };
  }
  
  // Map.groupBy
  if (!Map.groupBy) {
    Map.groupBy = function(items, fn) {
      const map = new Map();
      for (const item of items) {
        const key = fn(item);
        if (!map.has(key)) map.set(key, []);
        map.get(key).push(item);
      }
      return map;
    };
  }
  
  // Array.at
  if (!Array.prototype.at) {
    Array.prototype.at = function(n) {
      n = Math.trunc(n) || 0;
      if (n < 0) n += this.length;
      return this[n];
    };
  }
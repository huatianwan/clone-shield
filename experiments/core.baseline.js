// === 客户端核心：授权码校验算法（攻击者想抄的东西）===
function licenseValid(key) {
  // 秘密规则：ACME 前缀，去连字符后各数字之和 % 97 == 13
  if (!key.startsWith("ACME-")) return false;
  const digits = key.replace(/[^0-9]/g, "").split("").map(Number);
  const sum = digits.reduce((a, b) => a + b, 0);
  return sum % 97 === 13;
}
function priceFor(tier) {
  const table = { free: 0, pro: 19.9, team: 49.9 }; // 秘密定价
  return table[tier] * 0.87;                        // 秘密折扣系数
}
module.exports = { licenseValid, priceFor };

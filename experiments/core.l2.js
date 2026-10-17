// === L2 加固后的客户端：算法已搬服务端，这里只剩转发 ===
// 攻击者反编译这个文件，拿不到任何秘密规则——因为规则根本不在客户端。
async function licenseValid(key) {
  const r = await fetch("https://api.example.com/v1/license/verify", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-App-Attest": await attest() },
    body: JSON.stringify({ key })
  });
  const { valid } = await r.json();   // 服务端算完只回一个布尔
  return valid;
}
async function priceFor(tier) {
  const r = await fetch("https://api.example.com/v1/pricing/" + encodeURIComponent(tier), {
    headers: { "X-App-Attest": await attest() }
  });
  const { price } = await r.json();   // 只回最终价，不回定价表/折扣系数
  return price;
}
module.exports = { licenseValid, priceFor };

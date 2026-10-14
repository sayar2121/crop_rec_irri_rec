"""
Generate a clean, high-contrast, perfectly spaced IEEE/ACM research diagram for:
Blockchain Node Access Control & Registration Lifecycle (ECDSA secp256k1)
With Smart Contract state mapping: Register -> Approve / Deny / Revoke
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(17, 9.5), dpi=300)
ax.set_xlim(0, 17)
ax.set_ylim(0, 9.5)
ax.axis('off')

# Clean academic color palette
c_blue_bg = "#eff6ff"
c_blue_border = "#2563eb"
c_green_bg = "#f0fdf4"
c_green_border = "#16a34a"
c_red_bg = "#fef2f2"
c_red_border = "#dc2626"
c_orange_bg = "#fff7ed"
c_orange_border = "#ea580c"
c_purple_bg = "#faf5ff"
c_purple_border = "#7c3aed"
c_gray_bg = "#f8fafc"
c_gray_border = "#475569"

# Header
ax.text(8.5, 9.0, "Blockchain Node Access Control & Registration Lifecycle (ECDSA secp256k1)", 
        ha='center', va='center', fontsize=16, weight='bold', color='#0f172a')
ax.text(8.5, 8.65, "Cryptographic Node Authentication with Smart Contract State Mapping: Register -> Approve / Deny / Revoke", 
        ha='center', va='center', fontsize=11, color='#475569', style='italic')

def draw_card(x, y, w, h, title, lines=None, bg=c_blue_bg, border=c_blue_border, text_color="#0f172a", title_size=10.5):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.15", 
                                 facecolor=bg, edgecolor=border, linewidth=1.6, zorder=2)
    ax.add_patch(rect)
    if not lines:
        ax.text(x + w/2, y + h/2, title, ha='center', va='center', fontsize=title_size, weight='bold', color=text_color, zorder=3)
    else:
        ax.text(x + w/2, y + h - 0.28, title, ha='center', va='top', fontsize=title_size, weight='bold', color=text_color, zorder=3)
        line_str = "\n".join(lines)
        ax.text(x + w/2, y + 0.25, line_str, ha='center', va='bottom', fontsize=8.2, color='#334155', zorder=3, linespacing=1.3)

# 1. Left Tier: Dew Node (Sensors & Keypair)
card_dew = patches.FancyBboxPatch((0.5, 1.2), 3.4, 6.8, boxstyle="round,pad=0.15,rounding_size=0.2", 
                                  facecolor=c_gray_bg, edgecolor=c_gray_border, linewidth=1.8, zorder=1)
ax.add_patch(card_dew)
ax.text(2.2, 7.6, "IoT Dew Node\n(Keypad / Smartphone)", ha='center', va='center', fontsize=11.5, weight='bold', color='#0f172a')

draw_card(0.7, 5.8, 3.0, 1.4, "1. Keypair Generation", 
          ["Curve: secp256k1", "Private Key: d (Kept Secure)", "Public Key: Q = d * G"],
          bg=c_purple_bg, border=c_purple_border)

draw_card(0.7, 3.9, 3.0, 1.5, "2. Registration Request", 
          ["Payload: {NodeID, DevType, Tstamp}", "MsgHash = SHA-256(Payload)", "Sig = ECDSA_Sign(d, MsgHash)"],
          bg=c_blue_bg, border=c_blue_border)

draw_card(0.7, 1.6, 3.0, 1.9, "3. Outbound Transport", 
          ["Keypad: GSM AT Commands / SPI", "Smartphone: BLE 5.0 / SoftAP", "Broadcast to Blockchain Gateway"],
          bg="#ffffff", border="#94a3b8")

# Arrow from IoT Node to Blockchain
ax.annotate("", xy=(4.6, 4.65), xytext=(3.7, 4.65), arrowprops=dict(arrowstyle="->", lw=2.2, color="#2563eb"))
ax.text(4.15, 5.05, "submitRegistration()", ha='center', va='bottom', fontsize=8.8, weight='bold', color="#2563eb")
ax.text(4.15, 4.4, "{NodeID, PubKey, Sig}", ha='center', va='top', fontsize=7.8, color="#475569")

# 2. Top Authority: Administrator / Governance
draw_card(6.5, 7.3, 4.2, 1.0, "Network Authority / DAO", 
          ["Contract Owner / Multi-Sig Governance", "Controls Authorization & Key Revocation"],
          bg="#fef3c7", border="#d97706", title_size=10)

# 3. Center Tier: Smart Contract State Mapping Engine
center_card = patches.FancyBboxPatch((4.7, 1.2), 7.8, 5.8, boxstyle="round,pad=0.15,rounding_size=0.2", 
                                    facecolor="#ffffff", edgecolor="#334155", linewidth=2.0, linestyle="--", zorder=1)
ax.add_patch(center_card)
ax.text(8.6, 6.7, "Smart Contract Registry & Access Control Engine", ha='center', va='center', fontsize=12, weight='bold', color="#0f172a")

# Solidity Mapping Box
draw_card(5.0, 5.3, 7.2, 1.0, "mapping(address => NodeInfo) public nodeRegistry;", 
          ["enum NodeStatus { None, Pending, Active, Denied, Revoked }",
           "struct NodeInfo { NodeStatus status; bytes pubKey; uint256 registeredAt; }"],
          bg="#0f172a", border="#1e293b", text_color="#38bdf8", title_size=9.2)

# Lifecycle State Cards
# PENDING
draw_card(5.1, 3.6, 3.2, 1.3, "1. STATE: PENDING", 
          ["nodeRegistry[addr].status = Pending", "Sig format validated, awaiting review"],
          bg=c_blue_bg, border=c_blue_border)

# APPROVE
draw_card(8.7, 3.6, 3.2, 1.3, "2. STATE: ACTIVE (APPROVED)", 
          ["ECDSA_Verify(PubKey, Sig) == OK", "nodeRegistry[addr].status = Active"],
          bg=c_green_bg, border=c_green_border)

# DENY
draw_card(5.1, 1.6, 3.2, 1.4, "3. STATE: DENIED", 
          ["Sig failure / Unverified hardware", "nodeRegistry[addr].status = Denied"],
          bg=c_red_bg, border=c_red_border)

# REVOKE
draw_card(8.7, 1.6, 3.2, 1.4, "4. STATE: REVOKED", 
          ["Compromised node / Expired certificate", "nodeRegistry[addr].status = Revoked"],
          bg=c_orange_bg, border=c_orange_border)

# Transitions from Authority to Approve / Deny
ax.annotate("", xy=(6.7, 4.9), xytext=(7.8, 7.3), arrowprops=dict(arrowstyle="->", lw=1.6, color="#d97706", linestyle=":"))
ax.annotate("", xy=(10.3, 4.9), xytext=(9.4, 7.3), arrowprops=dict(arrowstyle="->", lw=1.6, color="#d97706", linestyle=":"))
ax.text(7.0, 6.1, "Policy Review", fontsize=8, weight='bold', color="#d97706")

# State transitions
ax.annotate("", xy=(8.7, 4.25), xytext=(8.3, 4.25), arrowprops=dict(arrowstyle="->", lw=2.0, color="#16a34a"))
ax.text(8.5, 4.45, "approve()", ha='center', fontsize=8.2, weight='bold', color="#16a34a")

ax.annotate("", xy=(6.7, 3.0), xytext=(6.7, 3.6), arrowprops=dict(arrowstyle="->", lw=2.0, color="#dc2626"))
ax.text(7.2, 3.3, "deny()", ha='center', fontsize=8.2, weight='bold', color="#dc2626")

ax.annotate("", xy=(10.3, 3.0), xytext=(10.3, 3.6), arrowprops=dict(arrowstyle="->", lw=2.0, color="#ea580c"))
ax.text(10.9, 3.3, "revoke()", ha='center', fontsize=8.2, weight='bold', color="#ea580c")

# 4. Right Tier: Data Ingestion Gatekeeper
right_card = patches.FancyBboxPatch((13.0, 1.2), 3.5, 6.8, boxstyle="round,pad=0.15,rounding_size=0.2", 
                                    facecolor=c_gray_bg, edgecolor=c_gray_border, linewidth=1.8, zorder=1)
ax.add_patch(right_card)
ax.text(14.75, 7.6, "Blockchain Ingestion Gate", ha='center', va='center', fontsize=11.5, weight='bold', color='#0f172a')

draw_card(13.2, 5.6, 3.1, 1.6, "Gatekeeper Verification", 
          ["require(nodeRegistry[sender]", " == NodeStatus.Active);", "Verifies ECDSA Sig per batch"],
          bg=c_purple_bg, border=c_purple_border)

draw_card(13.2, 3.6, 3.1, 1.6, "[PASS] Ingest Batch", 
          ["Committed to Ledger JSON", "Mined into new Blockchain Block", "Status: synced_and_anchored"],
          bg=c_green_bg, border=c_green_border)

draw_card(13.2, 1.6, 3.1, 1.6, "[DROP] Rejection", 
          ["Status: Denied / Revoked / None", "Emit UnauthorizedNodeEvent", "Packet Dropped (Zero Gas Cost)"],
          bg=c_red_bg, border=c_red_border)

# Connect Active State to Gatekeeper
ax.annotate("", xy=(13.0, 6.3), xytext=(11.9, 4.25), arrowprops=dict(arrowstyle="->", lw=2.2, color="#16a34a"))
ax.text(12.35, 5.5, "Active\nToken", ha='center', fontsize=8.2, weight='bold', color="#16a34a")

# Pass arrow
ax.annotate("", xy=(14.75, 5.2), xytext=(14.75, 5.6), arrowprops=dict(arrowstyle="->", lw=2.0, color="#16a34a"))
ax.text(15.2, 5.4, "Valid", fontsize=8.2, weight='bold', color="#16a34a")

# Block arrow from Deny/Revoke
ax.annotate("", xy=(13.2, 2.3), xytext=(11.9, 2.3), arrowprops=dict(arrowstyle="->", lw=2.0, color="#dc2626"))
ax.text(12.45, 2.5, "Blocked", ha='center', fontsize=8.2, weight='bold', color="#dc2626")

plt.tight_layout()
plt.savefig("blockchain_registration_access_control.png", dpi=300, bbox_inches='tight')
plt.close()
print("✅ Publication-ready diagram saved: blockchain_registration_access_control.png")

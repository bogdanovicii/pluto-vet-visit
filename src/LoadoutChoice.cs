using System.Collections.Generic;

namespace PlutoVetVisit
{
    /// <summary>Which starting guns Pluto gets back in the past (spec A7). The samurai costume (Pluto the Cat 2.16.0) starts
    /// with its alternate guns (pluto:taiyaki_cannon, pluto:katana) through startingAlternateGunIds; the normal skin keeps
    /// the Royal Kibble Sack.</summary>
    public static class LoadoutChoice
    {
        public static bool UseAlternate(PlayerController p)
        {
            return p != null && p.IsUsingAlternateCostume && p.startingAlternateGunIds != null && p.startingAlternateGunIds.Count > 0;
        }

        public static string Describe(PlayerController p)
        {
            if (p == null) return "no player";
            List<string> ids = new List<string>();
            if (p.startingAlternateGunIds != null) foreach (int id in p.startingAlternateGunIds) ids.Add(id.ToString());
            List<string> guns = new List<string>();
            if (p.inventory != null && p.inventory.AllGuns != null)
                foreach (Gun g in p.inventory.AllGuns) if (g != null) guns.Add(g.gunName + " #" + g.PickupObjectId);
            return "costume alt " + p.IsUsingAlternateCostume + ", alt gun ids [" + string.Join(",", ids.ToArray()) + "], guns [" + string.Join(", ", guns.ToArray()) + "]";
        }
    }
}

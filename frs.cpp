#include <bits/stdc++.h>

#include <nlohmann/json.hpp>
#include <ostream>

typedef long long ll;

bool validate_pick(
  std::string pick, const std::array<std::string, 7> & pick_order, const nlohmann::json & jadwal)
{
  if (pick.size() == 0) {
    return true;
  }

  int index = pick.size() - 1;
  char recent = pick.back();

  auto itr = jadwal.at(pick_order[index]).items().begin();
  while (itr.value().at("Kode").get<std::string>() != std::string(1, recent)) {
    ++itr;
  }

  int hari = itr.value().at("Hari").get<int>();
  int jam = itr.value().at("Jam").get<int>();

  for (int i = 0; i < pick.size() - 1; i++) {
    auto kelas = jadwal.at(pick_order[i]).items().begin();
    while (kelas.value().at("Kode").get<std::string>() != std::string(1, pick[i])) {
      ++kelas;
    }

    int hari_kelas = kelas.value().at("Hari").get<int>();
    int jam_kelas = kelas.value().at("Jam").get<int>();

    if (hari == hari_kelas && jam == jam_kelas) {
      return false;
    }
  }

  return true;
}

std::pair<std::string, int> backtrack(std::string pick, int val, int i,
  const std::array<std::string, 7> & pick_order, const nlohmann::json & jadwal)
{
  if (i >= pick_order.size()) {
    return std::make_pair(pick, val);
  }

  if (!validate_pick(pick, pick_order, jadwal)) {
    return std::make_pair("", 0);
  }

  if (jadwal.find(pick_order[i]) == jadwal.end()) {
    return backtrack(pick + 'x', val, i + 1, pick_order, jadwal);
  }

  std::pair<std::string, int> best = {"", 0};
  for (auto & [key, item] : jadwal.at(pick_order[i]).items()) {
    auto result = backtrack(pick + item.at("Kode").get<std::string>(),
      val + item.at("Rating").get<int>(), i + 1, pick_order, jadwal);
    // std::cout << result.first << " " << result.second << std::endl;

    if (result.second > best.second) {
      best = result;
    }
  }

  return best;
}

int main()
{
  std::ifstream ifs("jadwal.json");
  nlohmann::json jadwal = nlohmann::json::parse(ifs);

  std::array<std::string, 7> pick_order = {"PAA", "ProgJar", "MBD", "PM", "Probstat", "Otomata", "PPL"};

  auto result = backtrack("", 0, 0, pick_order, jadwal);
  std::cout << result.first << ' ' << result.second << std::endl;
}

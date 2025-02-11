#include <bits/stdc++.h>

#include <algorithm>
#include <nlohmann/json.hpp>

typedef long long ll;

bool validate_pick(
  std::string pick, const std::vector<std::string> & pick_order, const nlohmann::json & jadwal)
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
    int jumlah_murid = kelas.value().at("Jumlah Murid").get<int>();
    int max_murid = kelas.value().at("Max Murid").get<int>();

    if (hari == hari_kelas && jam == jam_kelas) {
      return false;
    }

    if (jumlah_murid == max_murid) {
      return false;
    }
  }

  return true;
}

std::pair<std::string, int> backtrack(std::string pick, int val, int i,
  const std::vector<std::string> & pick_order, const nlohmann::json & jadwal)
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

void frs_solver(const std::vector<std::string> & pick_order)
{
  std::ifstream ifs("jadwal.json");
  nlohmann::json jadwal = nlohmann::json::parse(ifs);
  ifs.close();

  auto result = backtrack("", 0, 0, pick_order, jadwal);

  for (auto i : pick_order) {
    std::cout << i << "\t";
  }
  std::cout << std::endl;

  int index = 0;
  for (auto i : result.first) {
    std::cout << i << "\t";
    for (int j = 8; j <= pick_order[index].size(); j += 8) {
      std::cout << "\t";
    }

    index++;
  }
  std::cout << std::endl;

  std::cout << "Max Rating : " << result.second << std::endl;
}

void update_pick_order(std::vector<std::string> & pick_order)
{
  std::ifstream ifs("pick_order.json");
  nlohmann::json json_order = nlohmann::json::parse(ifs);
  ifs.close();

  pick_order.clear();
  for (const auto & item : json_order) {
    pick_order.push_back(item.get<std::string>());
  }
}

int main(int argc, char ** argv)
{
  if (argc < 2) {
    std::cerr << "Please input delay time (ms) (0 for one time output)" << std::endl;
    return -1;
  }

  std::vector<std::string> pick_order;

  if (std::stoi(argv[1]) == 0) {
    update_pick_order(pick_order);
    frs_solver(pick_order);
    return 0;
  }

  while (true) {
    auto start = std::chrono::high_resolution_clock::now();

    update_pick_order(pick_order);
    frs_solver(pick_order);

    auto stop = std::chrono::high_resolution_clock::now();

    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(stop - start);
    std::cout << "FRS calculation took " << duration.count() << "ms" << std::endl;
    std::cout << std::endl;

    auto sleep_duration = std::chrono::milliseconds(std::stoi(argv[1])) - duration;
    if (sleep_duration.count() > 0) {
      std::this_thread::sleep_for(sleep_duration);
    }
  }
}

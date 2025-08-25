package com.mycompany.mavenproject3;

import com.fasterxml.jackson.databind.ObjectMapper;
import modelVessel.IterationStats;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;

import java.util.concurrent.*;
import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.ConcurrentHashMap;

@RestController
@RequestMapping("/api/simulation")
@CrossOrigin(origins = "*")
public class SimulationController {

    private final ObjectMapper objectMapper = new ObjectMapper();
    private final ExecutorService executorService = Executors.newFixedThreadPool(10);
    private final AtomicInteger requestCounter = new AtomicInteger(0);
    private final Map<String, IterationStats> resultsCache = new ConcurrentHashMap<>();

    @PostMapping("/run")
    public ResponseEntity<Map<String, Object>> runSimulation(@RequestBody Map<String, Object> request) {
        try {
            // Extract parameters from request
            Iteration iteration = new Iteration();
            iteration.setVarOfWork((Integer) request.getOrDefault("varOfWork", 3))
                    .setCapacityOfMainConveyor((Integer) request.getOrDefault("capacityOfMainConveyor", 800))
                    .setQuantityOfVagonsToSilageAtOnce((Integer) request.getOrDefault("quantityOfVagonsToSilageAtOnce", 8))
                    .setQuantityOfVehicleDischargeStations((Integer) request.getOrDefault("quantityOfVehicleDischargeStations", 2))
                    .setNumberOfVehicleSilages((Integer) request.getOrDefault("numberOfVehicleSilages", 2))
                    .setCapacityOfVehicleSilages((Integer) request.getOrDefault("capacityOfVehicleSilages", 800))
                    .setQuantityOfSilages((Integer) request.getOrDefault("quantityOfSilages", 17))
                    .setYearsModelWorking((Integer) request.getOrDefault("yearsModelWorking", 1));

            // Generate unique ID for this simulation
            String simulationId = "sim_" + requestCounter.incrementAndGet() + "_" + System.currentTimeMillis();

            // Run simulation asynchronously
            Future<IterationStats> future = executorService.submit(() -> {
                return IterationCallable.runExperiment(iteration);
            });

            // Wait for result with timeout
            IterationStats result;
            try {
                result = future.get(5, TimeUnit.MINUTES);
            } catch (TimeoutException e) {
                future.cancel(true);
                return ResponseEntity.status(HttpStatus.REQUEST_TIMEOUT)
                        .body(Map.of("error", "Simulation timed out"));
            } catch (Exception e) {
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                        .body(Map.of("error", "Simulation failed: " + e.getMessage()));
            }

            // Store result in cache
            resultsCache.put(simulationId, result);

            // Prepare response with KPIs
            Map<String, Object> response = new HashMap<>();
            response.put("simulationId", simulationId);
            response.put("vesselsHandledQtt", result.physicalStats.shipmentStats.vesselsHandledQtt);
            response.put("primeCost", result.economicStats.primeCost);
            response.put("handlingTime", result.physicalStats.shipmentStats.medianHandlingTime - result.physicalStats.shipmentStats.medianAtTerminalTime);
            response.put("profit", result.economicStats.income - result.economicStats.costs.total);
            response.put("timeAtTerminal", result.physicalStats.shipmentStats.medianAtTerminalTime);
            
            // Add additional metrics
            response.put("income", result.economicStats.income);
            response.put("totalCosts", result.economicStats.costs.total);
            response.put("medianHandlingTime", result.physicalStats.shipmentStats.medianHandlingTime);
            response.put("medianAtTerminalTime", result.physicalStats.shipmentStats.medianAtTerminalTime);

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Failed to run simulation: " + e.getMessage()));
        }
    }

    @GetMapping("/results/{simulationId}")
    public ResponseEntity<Map<String, Object>> getResults(@PathVariable String simulationId) {
        IterationStats result = resultsCache.get(simulationId);
        if (result == null) {
            return ResponseEntity.notFound().build();
        }

        Map<String, Object> response = new HashMap<>();
        response.put("simulationId", simulationId);
        response.put("vesselsHandledQtt", result.physicalStats.shipmentStats.vesselsHandledQtt);
        response.put("primeCost", result.economicStats.primeCost);
        response.put("handlingTime", result.physicalStats.shipmentStats.medianHandlingTime - result.physicalStats.shipmentStats.medianAtTerminalTime);
        response.put("profit", result.economicStats.income - result.economicStats.costs.total);
        response.put("timeAtTerminal", result.physicalStats.shipmentStats.medianAtTerminalTime);

        return ResponseEntity.ok(response);
    }

    @GetMapping("/all-results")
    public ResponseEntity<List<Map<String, Object>>> getAllResults() {
        List<Map<String, Object>> allResults = new ArrayList<>();
        
        for (Map.Entry<String, IterationStats> entry : resultsCache.entrySet()) {
            IterationStats result = entry.getValue();
            Map<String, Object> response = new HashMap<>();
            response.put("simulationId", entry.getKey());
            response.put("vesselsHandledQtt", result.physicalStats.shipmentStats.vesselsHandledQtt);
            response.put("primeCost", result.economicStats.primeCost);
            response.put("handlingTime", result.physicalStats.shipmentStats.medianHandlingTime - result.physicalStats.shipmentStats.medianAtTerminalTime);
            response.put("profit", result.economicStats.income - result.economicStats.costs.total);
            response.put("timeAtTerminal", result.physicalStats.shipmentStats.medianAtTerminalTime);
            
            allResults.add(response);
        }
        
        return ResponseEntity.ok(allResults);
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of("status", "healthy", "message", "Simulation service is running"));
    }

    @DeleteMapping("/clear-cache")
    public ResponseEntity<Map<String, String>> clearCache() {
        resultsCache.clear();
        return ResponseEntity.ok(Map.of("message", "Cache cleared successfully"));
    }
}

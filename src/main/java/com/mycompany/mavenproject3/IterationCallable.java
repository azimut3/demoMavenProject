package com.mycompany.mavenproject3;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.AllArgsConstructor;
import lombok.SneakyThrows;
import modelVessel.CustomExperiment;
import modelVessel.IterationStats;
import java.util.Random;

import java.io.FileOutputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Random;
import java.util.concurrent.Callable;


@AllArgsConstructor
public class IterationCallable implements Callable<IterationStats>, Serializable {
    private Path configRanFile;
    private Path statsFile;
    private Iteration iteration;

    @SneakyThrows
    public IterationStats call() {

        IterationStats iterationStats = runExperiment(iteration);

        //cargoTranshipmentCost averageAnnualProffit medianShipmentPendingTime medianHandlingTime
        String tablePattern = "%s; %s; %s; %s; %s";
        String dataCombination = String.format(
                tablePattern,
                iterationStats.physicalStats.shipmentStats.vesselsHandledQtt,
                round(iterationStats.economicStats.primeCost, 2),
                round((iterationStats.physicalStats.shipmentStats.medianHandlingTime - iterationStats.physicalStats.shipmentStats.medianAtTerminalTime), 2),
                round((iterationStats.economicStats.income - iterationStats.economicStats.costs.total), 2),
                round(iterationStats.physicalStats.shipmentStats.medianAtTerminalTime, 2)
        );

        //iterationString.add(dataCombination);

        ObjectMapper objectMapper = new ObjectMapper();
        Files.writeString(configRanFile,
                objectMapper.writeValueAsString(iteration) + System.lineSeparator(),
                StandardOpenOption.CREATE,
                StandardOpenOption.APPEND);
        Files.writeString(statsFile,
                iteration.toForeignKey() + ";" + dataCombination.toString() + System.lineSeparator(),
                StandardOpenOption.CREATE,
                StandardOpenOption.APPEND);

        return iterationStats;
    }


    public static double round(double value, int places) {
        double scale = Math.pow(10, places);
        return Math.round(value * scale) / scale;
    }
    
    private static void validateParameters(Iteration iteration) {
        // Check for null values
        if (iteration.getVarOfWork() == null || iteration.getCapacityOfMainConveyor() == null ||
            iteration.getQuantityOfVagonsToSilageAtOnce() == null || iteration.getQuantityOfVehicleDischargeStations() == null ||
            iteration.getNumberOfVehicleSilages() == null || iteration.getCapacityOfVehicleSilages() == null ||
            iteration.getQuantityOfSilages() == null || iteration.getYearsModelWorking() == null) {
            throw new IllegalArgumentException("All parameters must be non-null");
        }
        
        // Check parameter bounds
        if (iteration.getVarOfWork() < 1 || iteration.getVarOfWork() > 5) {
            throw new IllegalArgumentException("varOfWork must be between 1 and 5");
        }
        if (iteration.getCapacityOfMainConveyor() < 600 || iteration.getCapacityOfMainConveyor() > 1400) {
            throw new IllegalArgumentException("capacityOfMainConveyor must be between 600 and 1400");
        }
        if (iteration.getQuantityOfVagonsToSilageAtOnce() < 6 || iteration.getQuantityOfVagonsToSilageAtOnce() > 12) {
            throw new IllegalArgumentException("quantityOfVagonsToSilageAtOnce must be between 6 and 12");
        }
        if (iteration.getQuantityOfVehicleDischargeStations() < 1 || iteration.getQuantityOfVehicleDischargeStations() > 6) {
            throw new IllegalArgumentException("quantityOfVehicleDischargeStations must be between 1 and 6");
        }
        if (iteration.getNumberOfVehicleSilages() < 1 || iteration.getNumberOfVehicleSilages() > 6) {
            throw new IllegalArgumentException("numberOfVehicleSilages must be between 1 and 6");
        }
        if (iteration.getCapacityOfVehicleSilages() < 600 || iteration.getCapacityOfVehicleSilages() > 1200) {
            throw new IllegalArgumentException("capacityOfVehicleSilages must be between 600 and 1200");
        }
        if (iteration.getQuantityOfSilages() < 15 || iteration.getQuantityOfSilages() > 25) {
            throw new IllegalArgumentException("quantityOfSilages must be between 15 and 25");
        }
        if (iteration.getYearsModelWorking() < 1 || iteration.getYearsModelWorking() > 3) {
            throw new IllegalArgumentException("yearsModelWorking must be between 1 and 3");
        }
        
        System.out.println("Parameters validated successfully: " + iteration.toForeignKey());
    }

    public static IterationStats runExperiment(Iteration iteration) {
        try {
            // Validate parameters before running simulation
            validateParameters(iteration);
            
            // Try to create CustomExperiment with proper initialization
            CustomExperiment customExperiment;
            
            // Create CustomExperiment with null parameter (required by constructor)
            customExperiment = new CustomExperiment(null);
            
            // Set the parameters with validation
            customExperiment.varOfWork = Math.max(1, Math.min(5, iteration.getVarOfWork()));
            customExperiment.capacityOfMainConveyor = Math.max(600, Math.min(1400, iteration.getCapacityOfMainConveyor()));
            customExperiment.quantityOfVagonsToSilageAtOnce = Math.max(6, Math.min(12, iteration.getQuantityOfVagonsToSilageAtOnce()));
            customExperiment.quantityOfVehicleDischargeStations = Math.max(1, Math.min(6, iteration.getQuantityOfVehicleDischargeStations()));
            customExperiment.numberOfVehicleSilages = Math.max(1, Math.min(6, iteration.getNumberOfVehicleSilages()));
            customExperiment.capacityOfVehicleSilage = Math.max(600, Math.min(1200, iteration.getCapacityOfVehicleSilages()));
            customExperiment.quantityOfSilages = Math.max(15, Math.min(25, iteration.getQuantityOfSilages()));
            customExperiment.yearsModelWorking = Math.max(1, Math.min(3, iteration.getYearsModelWorking()));

            // Set random seed
            long seed = 3;
            Random notRandomSeed = new Random(seed);
            customExperiment.random = notRandomSeed;

            // Run the experiment
            customExperiment.run();
            System.out.println("==== Model Run End ===");
            System.out.println("Income: " + customExperiment.stats.economicStats.income);
            System.out.println("Profit: " + customExperiment.stats.economicStats.profit);
            System.out.println("Prime Cost: " + customExperiment.stats.economicStats.primeCost);
            System.out.println("Handling Time: " + customExperiment.stats.physicalStats.vesselStats.handlingTme);
            System.out.println("Time at Roads: " + customExperiment.stats.physicalStats.vesselStats.timeAtRoads);

            return customExperiment.stats;
            
        } catch (Exception e) {
            System.err.println("Error in runExperiment: " + e.getMessage());
            e.printStackTrace();
            throw new RuntimeException("Failed to run experiment: " + e.getMessage(), e);
        }
    }
}

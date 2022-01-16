package com.mycompany.mavenproject3;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.AllArgsConstructor;
import lombok.SneakyThrows;
import modelVessel.CustomExperiment;
import modelVessel.IterationStats;

import java.io.FileOutputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
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

    public static IterationStats runExperiment(Iteration iteration) {

        CustomExperiment customExperiment = new CustomExperiment(null);
        customExperiment.varOfWork = iteration.getVarOfWork();
        customExperiment.capacityOfMainConveyor = iteration.getCapacityOfMainConveyor();
        customExperiment.quantityOfVagonsToSilageAtOnce = iteration.getQuantityOfVagonsToSilageAtOnce();
        customExperiment.quantityOfVehicleDischargeStations = iteration.getQuantityOfVehicleDischargeStations();
        customExperiment.numberOfVehicleSilages = iteration.getNumberOfVehicleSilages();
        customExperiment.capacityOfVehicleSilage = iteration.getCapacityOfVehicleSilages();
        customExperiment.quantityOfSilages = iteration.getQuantityOfSilages();
        customExperiment.yearsModelWorking = iteration.getYearsModelWorking();

        customExperiment.run();
        System.out.println("==== Model Run End ===");
        System.out.println(customExperiment.stats.economicStats.income);
        System.out.println(customExperiment.stats.economicStats.profit);
        System.out.println(customExperiment.stats.economicStats.primeCost);
        System.out.println(customExperiment.stats.physicalStats.vesselStats.handlingTme);
        System.out.println(customExperiment.stats.physicalStats.vesselStats.timeAtRoads);

        return customExperiment.stats;
    }
}

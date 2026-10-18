/* -*-  Mode: C++; c-file-style: "gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2013 Centre Tecnologic de Telecomunicacions de Catalunya (CTTC)
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * Adapted from lena-x2-handover-measures.cc example from Manuel Requena
 *
 * Author: Manuel Requena <manuel.requena@cttc.es>
 */

/*
 * Network topology:
 *
 *      |     + --------------------------------------------------------->
 *      |     UE
 *      |
 *      |               d                   d                   d
 *    y |     |-------------------x-------------------x-------------------
 *      |     |                 eNodeB              eNodeB
 *      |   d |
 *      |     |
 *      |     |                                             d = x2Distance
 *            o (0, 0, 0)                                   y = yDistanceForUe
 */

#include <iostream>
#include <iomanip>
#include <fstream>
#include <string>
#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/lte-module.h"
#include "ns3/applications-module.h"
#include "ns3/point-to-point-module.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("LteTcpX2Handover");

// These variables are declared outside of main() so that they may be
// referenced in the callbacks below.  They are prefixed with "g_" to
// indicate global variable status.
std::ofstream g_ueMeasurements;
std::ofstream g_packetSinkRx;
std::ofstream g_cqiTrace;
std::ofstream g_tcpCongStateTrace;
std::ofstream g_positionTrace;

// Report on execution progress
void
ReportProgress (Time reportingInterval)
{
  std::cout << "*** Simulation time: " << std::fixed << std::setprecision (1) << Simulator::Now ().GetSeconds () << "s" << std::endl;
  Simulator::Schedule (reportingInterval, &ReportProgress, reportingInterval);
}

// Parse context strings of the form "/NodeList/3/DeviceList/1/Mac/Assoc"
// to extract the NodeId
uint32_t
ContextToNodeId (std::string context)
{
  std::string sub = context.substr (10);  // skip "/NodeList/"
  uint32_t pos = sub.find ("/Device");
  return atoi (sub.substr (0,pos).c_str ());
}

void
NotifyUdpReceived (std::string context, Ptr<const Packet> p, const Address &addr)
{
  std::cout << Simulator::Now ().GetSeconds () << " node "
            << ContextToNodeId (context)
            << " UDP received" << std::endl;
}

void
NotifyConnectionEstablishedUe (std::string context,
                               uint64_t imsi,
                               uint16_t cellid,
                               uint16_t rnti)
{
  std::cout << Simulator::Now ().GetSeconds () << " node "
            << ContextToNodeId (context)
            << " UE IMSI " << imsi
            << ": connected to CellId " << cellid
            << " with RNTI " << rnti
            << std::endl;
}

void
NotifyHandoverStartUe (std::string context,
                       uint64_t imsi,
                       uint16_t cellid,
                       uint16_t rnti,
                       uint16_t targetCellId)
{
  std::cout << Simulator::Now ().GetSeconds () << " node "
            << ContextToNodeId (context)
            << " UE IMSI " << imsi
            << ": previously connected to CellId " << cellid
            << " with RNTI " << rnti
            << ", doing handover to CellId " << targetCellId
            << std::endl;
}

void
NotifyHandoverEndOkUe (std::string context,
                       uint64_t imsi,
                       uint16_t cellid,
                       uint16_t rnti)
{
  std::cout << Simulator::Now ().GetSeconds () << " node "
            << ContextToNodeId (context)
            << " UE IMSI " << imsi
            << ": successful handover to CellId " << cellid
            << " with RNTI " << rnti
            << std::endl;
}

void
NotifyConnectionEstablishedEnb (std::string context,
                                uint64_t imsi,
                                uint16_t cellid,
                                uint16_t rnti)
{
  std::cout << Simulator::Now ().GetSeconds () << " node "
            << ContextToNodeId (context)
            << " eNB CellId " << cellid
            << ": successful connection of UE with IMSI " << imsi
            << " RNTI " << rnti
            << std::endl;
}

void
NotifyHandoverStartEnb (std::string context,
                        uint64_t imsi,
                        uint16_t cellid,
                        uint16_t rnti,
                        uint16_t targetCellId)
{
  std::cout << Simulator::Now ().GetSeconds () << " node "
            << ContextToNodeId (context)
            << " eNB CellId " << cellid
            << ": start handover of UE with IMSI " << imsi
            << " RNTI " << rnti
            << " to CellId " << targetCellId
            << std::endl;
}

void
NotifyHandoverEndOkEnb (std::string context,
                        uint64_t imsi,
                        uint16_t cellid,
                        uint16_t rnti)
{
  std::cout << Simulator::Now ().GetSeconds () << " node "
            << ContextToNodeId (context)
            << " eNB CellId " << cellid
            << ": completed handover of UE with IMSI " << imsi
            << " RNTI " << rnti
            << std::endl;
}

void
TracePosition (Ptr<Node> ue, Time interval)
{
  Vector v = ue->GetObject<MobilityModel> ()->GetPosition ();
  g_positionTrace << std::setw (7) << std::setprecision (3) << std::fixed << Simulator::Now ().GetSeconds () << " " 
    << v.x << " " << v.y << std::endl;
  Simulator::Schedule (interval, &TracePosition, ue, interval);
}

void
NotifyUeMeasurements (std::string context, uint16_t rnti, uint16_t cellId, double rsrpDbm, double rsrqDbm, bool servingCell, uint8_t ccId)
{
  g_ueMeasurements << std::setw (7) << std::setprecision (3) << std::fixed << Simulator::Now ().GetSeconds () << " " 
    << std::setw (3) << cellId << " " 
    << std::setw (3) << (servingCell ? "1" : "0") << " " 
    << std::setw (8) << rsrpDbm << " " 
    << std::setw (8) << rsrqDbm << std::endl;
}

void
NotifyPacketSinkRx (std::string context, Ptr<const Packet> packet, const Address &address)
{
  g_packetSinkRx << std::setw (7) << std::setprecision (3) << std::fixed << Simulator::Now ().GetSeconds () 
    << " " << std::setw (5) << packet->GetSize () << std::endl;
}

void
NotifyCqiReport (std::string context, uint16_t rnti, uint8_t cqi)
{
  g_cqiTrace << std::setw (7) << std::setprecision (3) << std::fixed << Simulator::Now ().GetSeconds () << " "
    << std::setw (4) << ContextToNodeId (context) << " "
    << std::setw (4) << rnti  << " " 
    << std::setw (3) << static_cast<uint16_t> (cqi) << std::endl;
}

void
CongStateTrace (const TcpSocketState::TcpCongState_t oldValue, const TcpSocketState::TcpCongState_t newValue)
{
  g_tcpCongStateTrace << std::setw (7) << std::setprecision (3) << std::fixed << Simulator::Now ().GetSeconds () << " "
    << std::setw (4) << TcpSocketState::TcpCongStateName[newValue] << std::endl;
}

void
ConnectTcpTrace (void)
{
  Config::ConnectWithoutContext ("/NodeList/1/$ns3::TcpL4Protocol/SocketList/0/CongState", MakeCallback (&CongStateTrace));
}

/**
 * Program for an automatic X2-based handover based on the RSRQ measures.
 * It instantiates two eNodeB, attaches one UE to the 'source' eNB.
 * The UE moves between both eNBs, it reports measures to the serving eNB and
 * the 'source' (serving) eNB triggers the handover of the UE towards
 * the 'target' eNB when it considers it is a better eNB.
 */
int
main (int argc, char *argv[])
{
  // Constants for this program (program is not designed to change these)
  uint16_t numberOfUes = 1;
  uint16_t numberOfEnbs = 2;

  // Constants that can be changed by command-line arguments
  double x2Distance = 500.0; // m
  double yDistanceForUe = 1000.0;   // m
  double speed = 20;       // m/s
  double enbTxPowerDbm = 46.0;
  std::string handoverType = "A2A4";
  bool useRlcUm = false;
  bool verbose = false;
  bool pcap = false;

  // Additional constants (not changeable at command line)
  LogLevel logLevel = (LogLevel)(LOG_PREFIX_ALL | LOG_LEVEL_ALL);
  std::string traceFilePrefix = "lte-tcp-x2-handover";
  Time positionTracingInterval = Seconds (5);
  Time reportingInterval = Seconds (10);
  uint32_t ftpSize = 200000000; // 200 MB
  uint16_t port = 4000;  // port number

  // change some default attributes so that they are reasonable for
  // this scenario, but do this before processing command line
  // arguments, so that the user is allowed to override these settings
  Config::SetDefault ("ns3::LteHelper::UseIdealRrc", BooleanValue (true));

  // Command line arguments
  CommandLine cmd;
  cmd.AddValue ("speed", "Speed of the UE (m/s)", speed);
  cmd.AddValue ("x2Distance", "Distance between eNB at X2 (meters)", x2Distance);
  cmd.AddValue ("yDistanceForUe", "y value (meters) for UE", yDistanceForUe);
  cmd.AddValue ("enbTxPowerDbm", "TX power (dBm) used by eNBs", enbTxPowerDbm);
  cmd.AddValue ("useRlcUm", "Use LTE RLC UM mode", useRlcUm);
  cmd.AddValue ("handoverType", "Handover type (A2A4 or A3Rsrp)", handoverType);
  cmd.AddValue ("pcap", "Enable pcap tracing", pcap);
  cmd.AddValue ("verbose", "Enable verbose logging", verbose);

  cmd.Parse (argc, argv);

  double simTime = 50; // seconds, for stationary simulation
  // Adjust based on speed, if motion is enabledj
  if (speed < 10 && speed != 0)
    {
      std::cout << "Select a speed at least 10 m/s, or zero" << std::endl;
      exit (1);
    }
  else if (speed >= 10)
    {
      // Handover around the middle of the total simTime
      simTime = (double)(numberOfEnbs + 1) * x2Distance / speed;
    }

  if (verbose)
    {
      LogComponentEnable ("EpcX2", logLevel);
      LogComponentEnable ("A2A4RsrqHandoverAlgorithm", logLevel);
      LogComponentEnable ("A3RsrpHandoverAlgorithm", logLevel);
    }

  if (useRlcUm == false)
    {
      Config::SetDefault ("ns3::LteEnbRrc::EpsBearerToRlcMapping", EnumValue (LteEnbRrc::RLC_AM_ALWAYS));
    }

  g_ueMeasurements.open ((traceFilePrefix + ".ue-measurements.dat").c_str(), std::ofstream::out);
  g_ueMeasurements << "# time   cellId   isServingCell?  RSRP(dBm)  RSRQ(dB)" << std::endl;
  g_packetSinkRx.open ((traceFilePrefix + ".tcp-receive.dat").c_str(), std::ofstream::out);
  g_packetSinkRx << "# time   bytesRx" << std::endl;
  g_cqiTrace.open ((traceFilePrefix + ".cqi.dat").c_str(), std::ofstream::out);
  g_cqiTrace << "# time   nodeId   rnti  cqi" << std::endl;
  g_tcpCongStateTrace.open ((traceFilePrefix + ".tcp-state.dat").c_str(), std::ofstream::out);
  g_tcpCongStateTrace << "# time   congState" << std::endl;
  g_positionTrace.open ((traceFilePrefix + ".position.dat").c_str(), std::ofstream::out);
  g_positionTrace << "# time   congState" << std::endl;

  Ptr<LteHelper> lteHelper = CreateObject<LteHelper> ();
  Ptr<PointToPointEpcHelper> epcHelper = CreateObject<PointToPointEpcHelper> ();
  lteHelper->SetEpcHelper (epcHelper);
  lteHelper->SetSchedulerType ("ns3::RrFfMacScheduler");

  if (handoverType == "A2A4")
    {
      lteHelper->SetHandoverAlgorithmType ("ns3::A2A4RsrqHandoverAlgorithm");
      lteHelper->SetHandoverAlgorithmAttribute ("ServingCellThreshold",
                                                UintegerValue (30));
      lteHelper->SetHandoverAlgorithmAttribute ("NeighbourCellOffset",
                                                UintegerValue (1));
    }
  else if (handoverType == "A3Rsrp")
    {
      lteHelper->SetHandoverAlgorithmType ("ns3::A3RsrpHandoverAlgorithm");
      lteHelper->SetHandoverAlgorithmAttribute ("Hysteresis",
                                                 DoubleValue (3.0));
      lteHelper->SetHandoverAlgorithmAttribute ("TimeToTrigger",
                                                 TimeValue (MilliSeconds (256)));
    }
  else
    {
      std::cout << "Unknown handover type: " << handoverType << std::endl;
      exit (1);
    }

  // Create a single RemoteHost
  NodeContainer remoteHostContainer;
  remoteHostContainer.Create (1);
  Ptr<Node> remoteHost = remoteHostContainer.Get (0);
  InternetStackHelper internet;
  internet.Install (remoteHostContainer);

  // Create the notional Internet
  PointToPointHelper p2ph;
  p2ph.SetDeviceAttribute ("DataRate", DataRateValue (DataRate ("100Gb/s")));
  p2ph.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2ph.SetChannelAttribute ("Delay", TimeValue (Seconds (0.010)));
  NetDeviceContainer internetDevices = p2ph.Install (epcHelper->GetPgwNode (), remoteHost);
  Ipv4AddressHelper ipv4h;
  ipv4h.SetBase ("1.0.0.0", "255.0.0.0");
  Ipv4InterfaceContainer internetIpIfaces = ipv4h.Assign (internetDevices);
  //Ipv4Address remoteHostAddr = internetIpIfaces.GetAddress (1);

  // Routing of the Internet Host (towards the LTE network)
  Ipv4StaticRoutingHelper ipv4RoutingHelper;
  Ptr<Ipv4StaticRouting> remoteHostStaticRouting = ipv4RoutingHelper.GetStaticRouting (remoteHost->GetObject<Ipv4> ());
  // interface 0 is localhost, 1 is the p2p device
  remoteHostStaticRouting->AddNetworkRouteTo (Ipv4Address ("7.0.0.0"), Ipv4Mask ("255.0.0.0"), 1);

  NodeContainer ueNodes;
  NodeContainer enbNodes;
  enbNodes.Create (numberOfEnbs);
  ueNodes.Create (numberOfUes);

  // Install Mobility Model in eNB
  Ptr<ListPositionAllocator> enbPositionAlloc = CreateObject<ListPositionAllocator> ();
  for (uint16_t i = 0; i < numberOfEnbs; i++)
    {
      Vector enbPosition (x2Distance * (i + 1), x2Distance, 0);
      enbPositionAlloc->Add (enbPosition);
    }
  MobilityHelper enbMobility;
  enbMobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  enbMobility.SetPositionAllocator (enbPositionAlloc);
  enbMobility.Install (enbNodes);

  // Install Mobility Model in UE
  MobilityHelper ueMobility;
  ueMobility.SetMobilityModel ("ns3::ConstantVelocityMobilityModel");
  ueMobility.Install (ueNodes);
  ueNodes.Get (0)->GetObject<MobilityModel> ()->SetPosition (Vector (0, yDistanceForUe, 0));
  ueNodes.Get (0)->GetObject<ConstantVelocityMobilityModel> ()->SetVelocity (Vector (speed, 0, 0));

  // Install LTE Devices in eNB and UEs
  Config::SetDefault ("ns3::LteEnbPhy::TxPower", DoubleValue (enbTxPowerDbm));
  NetDeviceContainer enbLteDevs = lteHelper->InstallEnbDevice (enbNodes);
  NetDeviceContainer ueLteDevs = lteHelper->InstallUeDevice (ueNodes);

  // Install the IP stack on the UEs
  internet.Install (ueNodes);
  Ipv4InterfaceContainer ueIpIfaces;
  ueIpIfaces = epcHelper->AssignUeIpv4Address (NetDeviceContainer (ueLteDevs));

  // Attach all UEs to the first eNodeB
  for (uint16_t i = 0; i < numberOfUes; i++)
    {
      lteHelper->Attach (ueLteDevs.Get (i), enbLteDevs.Get (0));
    }

  Ptr<Ipv4StaticRouting> ueStaticRouting = ipv4RoutingHelper.GetStaticRouting (ueNodes.Get (0)->GetObject<Ipv4> ());
  ueStaticRouting->SetDefaultRoute (epcHelper->GetUeDefaultGatewayAddress (), 1);
  BulkSendHelper ftpServer ("ns3::TcpSocketFactory", Address ());
  
  AddressValue remoteAddress (InetSocketAddress (ueIpIfaces.GetAddress (0), port));
  ftpServer.SetAttribute ("Remote", remoteAddress);
  ftpServer.SetAttribute ("MaxBytes", UintegerValue (ftpSize));
  NS_LOG_LOGIC ("setting up TCP flow from remote host to UE");
  ApplicationContainer sourceApp = ftpServer.Install (remoteHost);
  sourceApp.Start (Seconds (1));
  sourceApp.Stop (Seconds (simTime));

  Address sinkLocalAddress (InetSocketAddress (Ipv4Address::GetAny (), port));
  PacketSinkHelper sinkHelper ("ns3::TcpSocketFactory", sinkLocalAddress);
  ApplicationContainer sinkApp = sinkHelper.Install (ueNodes.Get (0));
  sinkApp.Start (Seconds (1));
  sinkApp.Stop (Seconds (simTime));

  Ptr<EpcTft> tft = Create<EpcTft> ();
  EpcTft::PacketFilter dlpf;
  dlpf.localPortStart = port;
  dlpf.localPortEnd = port;
  tft->Add (dlpf);
  EpsBearer bearer (EpsBearer::NGBR_VIDEO_TCP_DEFAULT);
  lteHelper->ActivateDedicatedEpsBearer (ueLteDevs.Get (0), bearer, tft);

  // Add X2 interface
  lteHelper->AddX2Interface (enbNodes);

  // Tracing
  if (pcap)
    {
      p2ph.EnablePcapAll ("lte-tcp-x2-handover");
    }

  lteHelper->EnablePhyTraces ();
  lteHelper->EnableMacTraces ();
  lteHelper->EnableRlcTraces ();
  lteHelper->EnablePdcpTraces ();
  Ptr<RadioBearerStatsCalculator> rlcStats = lteHelper->GetRlcStats ();
  rlcStats->SetAttribute ("EpochDuration", TimeValue (Seconds (1.0)));
  Ptr<RadioBearerStatsCalculator> pdcpStats = lteHelper->GetPdcpStats ();
  pdcpStats->SetAttribute ("EpochDuration", TimeValue (Seconds (1.0)));

  // connect custom trace sinks for RRC connection establishment and handover notification
  Config::Connect ("/NodeList/*/DeviceList/*/LteEnbRrc/ConnectionEstablished",
                   MakeCallback (&NotifyConnectionEstablishedEnb));
  Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/ConnectionEstablished",
                   MakeCallback (&NotifyConnectionEstablishedUe));
  Config::Connect ("/NodeList/*/DeviceList/*/LteEnbRrc/HandoverStart",
                   MakeCallback (&NotifyHandoverStartEnb));
  Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/HandoverStart",
                   MakeCallback (&NotifyHandoverStartUe));
  Config::Connect ("/NodeList/*/DeviceList/*/LteEnbRrc/HandoverEndOk",
                   MakeCallback (&NotifyHandoverEndOkEnb));
  Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/HandoverEndOk",
                   MakeCallback (&NotifyHandoverEndOkUe));
  // connect additional traces for more experiment tracing
  Config::Connect ("/NodeList/4/DeviceList/*/ComponentCarrierMapUe/*/LteUePhy/ReportUeMeasurements",
                   MakeCallback (&NotifyUeMeasurements));
  Config::Connect ("/NodeList/4/ApplicationList/*/$ns3::PacketSink/Rx",
                   MakeCallback (&NotifyPacketSinkRx));
  Config::Connect ("/NodeList/*/DeviceList/*/$ns3::LteEnbNetDevice/ComponentCarrierMap/*/FfMacScheduler/$ns3::RrFfMacScheduler/WidebandCqiReport",
                   MakeCallback (&NotifyCqiReport));

  // Delay trace connection until TCP socket comes into existence
  Simulator::Schedule (Seconds (1.001), &ConnectTcpTrace);
  // Initiate position tracing
  Simulator::Schedule (Seconds (0), &TracePosition, ueNodes.Get(0), positionTracingInterval);

  // Start to execute the program
  Vector vUe = ueNodes.Get (0)->GetObject<MobilityModel> ()->GetPosition ();
  Vector vEnb1 = enbNodes.Get (0)->GetObject<MobilityModel> ()->GetPosition ();
  Vector vEnb2 = enbNodes.Get (1)->GetObject<MobilityModel> ()->GetPosition ();
  std::cout << "Initial positions:  UE: (" << vUe.x << "," << vUe.y << "), "
    << "eNB1: (" << vEnb1.x << "," << vEnb1.y << "), "
    << "eNB2: (" << vEnb2.x << "," << vEnb2.y << ")" << std::endl;
  std::cout << "Simulation time: " << simTime << " sec" << std::endl;

  Simulator::Schedule (reportingInterval, &ReportProgress, reportingInterval);
  
  Simulator::Stop (Seconds (simTime));
  Simulator::Run ();

  // This method coordinates the deallocation of heap memory so that no
  // memory leaks are reported.
  Simulator::Destroy ();

  // Close any open file descriptors
  g_ueMeasurements.close ();
  g_cqiTrace.close ();
  g_packetSinkRx.close ();
  g_tcpCongStateTrace.close ();
  g_positionTrace.close ();

  return 0;
}

/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2018 University of Washington
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
 */

#include "ns3/test.h"
#include "ns3/snr-per-error-model.h"

using namespace ns3;

class SimpleWirelessSnrPerMethods : public TestCase
{
public:
  SimpleWirelessSnrPerMethods ();
  virtual ~SimpleWirelessSnrPerMethods ();

private:
  virtual void DoRun (void);
};

SimpleWirelessSnrPerMethods::SimpleWirelessSnrPerMethods ()
  : TestCase ("Check the SnrPerErrorModel basic methods (Q function, BER to PER)")
{
}

SimpleWirelessSnrPerMethods::~SimpleWirelessSnrPerMethods ()
{
}

void
SimpleWirelessSnrPerMethods::DoRun (void)
{
  Ptr<TableSnrPerErrorModel> model = CreateObject<TableSnrPerErrorModel> ();
  double valueToCheck = model->QFunction (0);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 0.5, 1e-4, "Numbers are not equal within tolerance");
  valueToCheck = model->QFunction (0.5);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 0.30854, 0.004, "Numbers are not equal within tolerance");
  valueToCheck = model->QFunction (1.0);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 0.15866, 0.002, "Numbers are not equal within tolerance");
  valueToCheck = model->QFunction (1.5);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 0.066807, 0.0001, "Numbers are not equal within tolerance");
  // Can add some more values later

  valueToCheck = model->BerToPer (0.0001, 1000);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 0.550689, 1e-6, "Numbers are not equal within tolerance");
}

class SimpleWirelessTableModel : public TestCase
{
public:
  SimpleWirelessTableModel ();
  virtual ~SimpleWirelessTableModel ();

private:
  virtual void DoRun (void);
};

SimpleWirelessTableModel::SimpleWirelessTableModel ()
  : TestCase ("Check the TableSnrPerErrorModel")
{
}

SimpleWirelessTableModel::~SimpleWirelessTableModel ()
{
}

void
SimpleWirelessTableModel::DoRun (void)
{
  Ptr<TableSnrPerErrorModel> model = CreateObject<TableSnrPerErrorModel> ();
  model->AddValue (-80, 1); 
  model->AddValue (-79, 0.75); 
  model->AddValue (-78, 0.5); 
  model->AddValue (-77, 0.25); 
  model->AddValue (-76, 0); 
  double valueToCheck = model->Receive (-80, 100);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 1, 1e-6, "Numbers are not equal within tolerance");
  // Check cached value
  valueToCheck = model->Receive (-80, 100);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 1, 1e-6, "Numbers are not equal within tolerance");
  valueToCheck = model->Receive (-76, 100);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 0, 1e-6, "Numbers are not equal within tolerance");
  valueToCheck = model->Receive (-78, 100);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 0.5, 1e-6, "Numbers are not equal within tolerance");
  valueToCheck = model->Receive (-77.5, 100);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 0.375, 1e-6, "Numbers are not equal within tolerance");
  valueToCheck = model->Receive (-82, 100);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 1, 1e-6, "Numbers are not equal within tolerance");
  valueToCheck = model->Receive (-60, 100);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 0, 1e-6, "Numbers are not equal within tolerance");

  model = 0;
  // Check unordered insertion on new model
  model = CreateObject<TableSnrPerErrorModel> ();
  model->AddValue (-77, 0.25); 
  model->AddValue (-80, 1); 
  model->AddValue (-78, 0.5); 
  model->AddValue (-79, 0.75); 
  model->AddValue (-76, 0); 
  valueToCheck = model->Receive (-80, 100);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 1, 1e-6, "Numbers are not equal within tolerance");
  // Check cached value
  valueToCheck = model->Receive (-80, 100);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 1, 1e-6, "Numbers are not equal within tolerance");
  valueToCheck = model->Receive (-76, 100);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 0, 1e-6, "Numbers are not equal within tolerance");
  valueToCheck = model->Receive (-78, 100);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 0.5, 1e-6, "Numbers are not equal within tolerance");
  valueToCheck = model->Receive (-77.5, 100);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 0.375, 1e-6, "Numbers are not equal within tolerance");
  valueToCheck = model->Receive (-82, 100);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 1, 1e-6, "Numbers are not equal within tolerance");
  valueToCheck = model->Receive (-60, 100);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 0, 1e-6, "Numbers are not equal within tolerance");

  model = 0;
  // Check empty model; should be PER of 1
  model = CreateObject<TableSnrPerErrorModel> ();
  valueToCheck = model->Receive (-60, 100);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 1, 1e-6, "Numbers are not equal within tolerance");
  valueToCheck = model->Receive (-80, 100);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 1, 1e-6, "Numbers are not equal within tolerance");
  valueToCheck = model->Receive (-100,100);
  NS_TEST_ASSERT_MSG_EQ_TOL (valueToCheck, 1, 1e-6, "Numbers are not equal within tolerance");
}

class SimpleWirelessTestSuite : public TestSuite
{
public:
  SimpleWirelessTestSuite ();
};

SimpleWirelessTestSuite::SimpleWirelessTestSuite ()
  : TestSuite ("simple-wireless", UNIT)
{
  AddTestCase (new SimpleWirelessSnrPerMethods, TestCase::QUICK);
  AddTestCase (new SimpleWirelessTableModel, TestCase::QUICK);
}

static SimpleWirelessTestSuite simpleWirelessTestSuite;

